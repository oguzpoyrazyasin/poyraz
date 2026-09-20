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
