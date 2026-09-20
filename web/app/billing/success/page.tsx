import Link from "next/link";
export default function BillingSuccessPage() {
  return <main className="legal"><h1>Ödeme işleme alındı.</h1><p>Ödeme sonucu güvenli PayTR callback'i üzerinden hesabınıza yansıtılır.</p><Link className="primaryButton" href="/dashboard">Panele dön</Link></main>;
}
