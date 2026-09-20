import crypto from "crypto";

const required = (name: string) => {
  const value = process.env[name];
  if (!value) throw new Error(`Missing environment variable: ${name}`);
  return value;
};

export function createPaytrToken(parts: Array<string | number>) {
  const merchantKey = required("PAYTR_MERCHANT_KEY");
  const merchantSalt = required("PAYTR_MERCHANT_SALT");
  const payload = parts.join("") + merchantSalt;
  return crypto.createHmac("sha256", merchantKey).update(payload).digest("base64");
}

export function verifyPaytrCallback(params: {
  merchant_oid: string;
  status: string;
  total_amount: string;
  hash: string;
}) {
  const merchantKey = required("PAYTR_MERCHANT_KEY");
  const merchantSalt = required("PAYTR_MERCHANT_SALT");
  const expected = crypto
    .createHmac("sha256", merchantKey)
    .update(params.merchant_oid + merchantSalt + params.status + params.total_amount)
    .digest("base64");

  const a = Buffer.from(expected);
  const b = Buffer.from(params.hash || "");
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

export type IframeCheckoutInput = {
  userIp: string;
  merchantOid: string;
  email: string;
  paymentAmountMinor: number;
  basketBase64: string;
  userName: string;
  userAddress: string;
  userPhone: string;
  okUrl: string;
  failUrl: string;
};

export async function createPaytrIframeToken(input: IframeCheckoutInput) {
  const merchantId = required("PAYTR_MERCHANT_ID");
  const merchantKey = required("PAYTR_MERCHANT_KEY");
  const merchantSalt = required("PAYTR_MERCHANT_SALT");
  const testMode = process.env.PAYTR_TEST_MODE === "0" ? "0" : "1";
  const noInstallment = "1";
  const maxInstallment = "0";
  const currency = "TL";

  const hashStr =
    merchantId +
    input.userIp +
    input.merchantOid +
    input.email +
    input.paymentAmountMinor +
    input.basketBase64 +
    noInstallment +
    maxInstallment +
    currency +
    testMode;

  const paytrToken = crypto
    .createHmac("sha256", merchantKey)
    .update(hashStr + merchantSalt)
    .digest("base64");

  const body = new URLSearchParams({
    merchant_id: merchantId,
    user_ip: input.userIp,
    merchant_oid: input.merchantOid,
    email: input.email,
    payment_amount: String(input.paymentAmountMinor),
    paytr_token: paytrToken,
    user_basket: input.basketBase64,
    debug_on: testMode === "1" ? "1" : "0",
    no_installment: noInstallment,
    max_installment: maxInstallment,
    user_name: input.userName.slice(0, 60),
    user_address: input.userAddress.slice(0, 400),
    user_phone: input.userPhone.slice(0, 20),
    merchant_ok_url: input.okUrl,
    merchant_fail_url: input.failUrl,
    timeout_limit: "30",
    currency,
    test_mode: testMode,
    lang: "tr"
  });

  const response = await fetch("https://www.paytr.com/odeme/api/get-token", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body,
    cache: "no-store"
  });

  if (!response.ok) throw new Error("PayTR token request failed.");
  const result = (await response.json()) as { status: string; token?: string; reason?: string };
  if (result.status !== "success" || !result.token) {
    throw new Error(result.reason || "PayTR iframe token could not be created.");
  }
  return result.token;
}
