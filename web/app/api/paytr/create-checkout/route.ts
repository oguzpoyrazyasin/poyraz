import crypto from "crypto";
import { NextRequest, NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { createSupabaseAdminClient } from "@/lib/supabase/admin";
import { createPaytrIframeToken } from "@/lib/paytr";
import { plans } from "@/lib/plans";

const validIntervals = new Set(["monthly", "annual"]);

function remoteIp(request: NextRequest) {
  const forwarded = request.headers.get("x-forwarded-for");
  return (forwarded?.split(",")[0] || request.headers.get("x-real-ip") || "127.0.0.1").trim();
}

export async function POST(request: NextRequest) {
  try {
    const supabase = await createSupabaseServerClient();
    const { data: authData } = await supabase.auth.getUser();
    if (!authData.user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

    const body = await request.json();
    const plan = plans.find(p => p.id === body.planId);
    const interval = validIntervals.has(body.interval) ? body.interval : "monthly";
    const phone = String(body.phone || "").trim();
    const address = String(body.address || "").trim();

    if (!plan || phone.length < 8 || address.length < 8) {
      return NextResponse.json({ error: "invalid_billing_details" }, { status: 400 });
    }

    const { data: profile } = await supabase
      .from("profiles")
      .select("full_name,email")
      .eq("id", authData.user.id)
      .single();

    const amountTry = interval === "annual" ? plan.annualPriceTry : plan.monthlyPriceTry;
    const paymentAmountMinor = amountTry * 100;
    const merchantOid = `PK${Date.now()}${crypto.randomBytes(5).toString("hex")}`.slice(0, 64);
    const basket = [[`Poyraz Kids ${plan.name} ${interval === "annual" ? "Yıllık" : "Aylık"}`, amountTry.toFixed(2), 1]];
    const basketBase64 = Buffer.from(JSON.stringify(basket), "utf8").toString("base64");

    const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || request.nextUrl.origin;
    const admin = createSupabaseAdminClient();

    const { error: updateError } = await admin
      .from("subscriptions")
      .update({
        plan_id: plan.id,
        billing_interval: interval,
        provider_order_id: merchantOid,
        updated_at: new Date().toISOString()
      })
      .eq("parent_id", authData.user.id);

    if (updateError) throw updateError;

    const token = await createPaytrIframeToken({
      userIp: remoteIp(request),
      merchantOid,
      email: profile?.email || authData.user.email || "",
      paymentAmountMinor,
      basketBase64,
      userName: profile?.full_name || "Poyraz Kids Parent",
      userAddress: address,
      userPhone: phone,
      okUrl: `${siteUrl}/billing/success`,
      failUrl: `${siteUrl}/billing/fail`
    });

    return NextResponse.json({
      token,
      iframeUrl: `https://www.paytr.com/odeme/guvenli/${token}`,
      merchantOid
    });
  } catch (error) {
    console.error("PAYTR_CHECKOUT", error);
    return NextResponse.json({ error: "checkout_unavailable" }, { status: 503 });
  }
}
