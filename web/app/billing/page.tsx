"use client";

import { useState } from "react";
import Link from "next/link";
import { plans } from "@/lib/plans";

export default function BillingPage() {
  const [planId, setPlanId] = useState("family");
  const [interval, setInterval] = useState<"monthly" | "annual">("monthly");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [iframeUrl, setIframeUrl] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);

  async function startCheckout() {
    setBusy(true);
    setError(false);
    try {
      const response = await fetch("/api/paytr/create-checkout", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ planId, interval, phone, address })
      });
      if (!response.ok) throw new Error("checkout");
      const data = await response.json();
      setIframeUrl(data.iframeUrl);
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="legal">
      <Link href="/dashboard">← Poyraz Kids paneline dön</Link>
      <h1>Üyeliğinizi seçin</h1>
      <p>3 günlük ücretsiz denemeden sonra yalnızca açıkça ödeme başlattığınızda tahsilat yapılır.</p>

      <div className="pricingGrid billingGrid">
        {plans.map(plan => (
          <button
            key={plan.id}
            type="button"
            className={`priceCard selectCard ${planId === plan.id ? "selected" : ""}`}
            onClick={() => setPlanId(plan.id)}
          >
            <h3>{plan.name}</h3>
            <div className="price"><b>₺{interval === "monthly" ? plan.monthlyPriceTry : plan.annualPriceTry}</b><span>{interval === "monthly" ? "/ ay" : "/ yıl"}</span></div>
            <p>{plan.childLimit} çocuk profiline kadar</p>
          </button>
        ))}
      </div>

      <div className="billingBox">
        <div className="toggleRow">
          <button type="button" className={interval === "monthly" ? "activeToggle" : ""} onClick={() => setInterval("monthly")}>Aylık</button>
          <button type="button" className={interval === "annual" ? "activeToggle" : ""} onClick={() => setInterval("annual")}>Yıllık</button>
        </div>

        <div className="field"><label>Ebeveyn telefon numarası</label><input value={phone} onChange={e => setPhone(e.target.value)} placeholder="+90 5xx xxx xx xx" /></div>
        <div className="field"><label>Fatura adresi</label><input value={address} onChange={e => setAddress(e.target.value)} placeholder="Fatura adresiniz" /></div>

        <button className="primaryButton full" type="button" onClick={startCheckout} disabled={busy}>
          {busy ? "Ödeme ekranı hazırlanıyor…" : "Güvenli ödemeye geç"}
        </button>
        <p className="formHint">Kart bilgileri Poyraz Kids'e gönderilmez; ödeme ekranı PayTR tarafından sunulur.</p>
        {error && <p className="errorNotice">Ödeme servisi şu anda başlatılamadı. Bilgileri ve entegrasyon ayarlarını kontrol edin.</p>}
      </div>

      {iframeUrl && (
        <section className="paytrFrameWrap">
          <h2>Güvenli ödeme</h2>
          <iframe title="PayTR Güvenli Ödeme" src={iframeUrl} className="paytrFrame" />
        </section>
      )}
    </main>
  );
}
