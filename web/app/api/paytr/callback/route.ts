import { NextRequest, NextResponse } from "next/server";
import { verifyPaytrCallback } from "@/lib/paytr";
import { createSupabaseAdminClient } from "@/lib/supabase/admin";

export async function POST(request: NextRequest) {
  const form = await request.formData();
  const params = {
    merchant_oid: String(form.get("merchant_oid") || ""),
    status: String(form.get("status") || ""),
    total_amount: String(form.get("total_amount") || "0"),
    hash: String(form.get("hash") || "")
  };

  if (!verifyPaytrCallback(params)) {
    return new NextResponse("BAD HASH", { status: 400 });
  }

  const supabase = createSupabaseAdminClient();
  const { data: subscription } = await supabase
    .from("subscriptions")
    .select("id,parent_id,billing_interval,status")
    .eq("provider_order_id", params.merchant_oid)
    .maybeSingle();

  if (!subscription) {
    return new NextResponse("ORDER NOT FOUND", { status: 404 });
  }

  const rawPayload = Object.fromEntries(
    Array.from(form.entries()).map(([key, value]) => [key, String(value)])
  );

  await supabase.from("payment_events").upsert(
    {
      merchant_oid: params.merchant_oid,
      parent_id: subscription.parent_id,
      status: params.status,
      amount_minor: Number(params.total_amount) || null,
      provider: "paytr",
      raw_payload: rawPayload
    },
    { onConflict: "provider,merchant_oid,status", ignoreDuplicates: true }
  );

  if (params.status === "success") {
    const now = new Date();
    const periodEnd = new Date(now);
    if (subscription.billing_interval === "annual") {
      periodEnd.setFullYear(periodEnd.getFullYear() + 1);
    } else {
      periodEnd.setMonth(periodEnd.getMonth() + 1);
    }

    await supabase
      .from("subscriptions")
      .update({
        status: "active",
        current_period_end: periodEnd.toISOString(),
        updated_at: now.toISOString()
      })
      .eq("id", subscription.id);
  } else if (subscription.status !== "trialing") {
    await supabase
      .from("subscriptions")
      .update({ status: "past_due", updated_at: new Date().toISOString() })
      .eq("id", subscription.id);
  }

  return new NextResponse("OK", {
    status: 200,
    headers: { "content-type": "text/plain; charset=utf-8" }
  });
}
