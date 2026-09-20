import Link from "next/link";
export default function BillingFailPage() {
  return <main className="legal"><h1>Ödeme tamamlanamadı.</h1><p>Herhangi bir abonelik aktivasyonu yapılmadı. Ödeme ekranını yeniden deneyebilirsiniz.</p><Link className="primaryButton" href="/billing">Tekrar dene</Link></main>;
}
