import Link from "next/link";
import { plans, TRIAL_DAYS } from "@/lib/plans";

export default function RegisterPage() {
  return (
    <main className="authPage">
      <section className="authAside">
        <Link className="brand" href="/"><span className="brandMark">P</span><span>Poyraz Kids</span></Link>
        <div>
          <div className="eyebrow light">İLK {TRIAL_DAYS} GÜN ÜCRETSİZ</div>
          <h1>Bir ebeveyn hesabıyla başlayın.</h1>
          <p>Deneme döneminde platformu keşfedin. Ücretli dönem başlamadan önce planınızı değiştirebilir veya üyeliğinizi iptal edebilirsiniz.</p>
        </div>
        <small>Kart bilgileri Poyraz Kids sunucularında tutulmaz.</small>
      </section>
      <section className="authCardWrap">
        <form className="authCard">
          <h2>Hesabınızı oluşturun.</h2>
          <p>Bu hesap ebeveyn veya yasal vasi tarafından oluşturulmalıdır.</p>
          <div className="field"><label>Ad soyad</label><input name="name" autoComplete="name" required /></div>
          <div className="field"><label>E-posta</label><input type="email" name="email" autoComplete="email" required /></div>
          <div className="field"><label>Şifre</label><input type="password" name="password" autoComplete="new-password" minLength={12} required /></div>
          <div className="field">
            <label>Plan</label>
            <select name="plan" defaultValue="family">
              {plans.map(p => <option value={p.id} key={p.id}>{p.name} — ₺{p.monthlyPriceTry}/ay</option>)}
            </select>
          </div>
          <button className="primaryButton full" type="submit">{TRIAL_DAYS} günlük denemeyi başlat</button>
          <p className="formHint">Devam ederek Kullanım Koşulları ve Gizlilik Politikası'nı kabul etmiş olursunuz.</p>
        </form>
      </section>
    </main>
  );
}
