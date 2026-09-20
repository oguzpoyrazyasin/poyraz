import Link from "next/link";

export default function LoginPage() {
  return (
    <main className="authPage">
      <section className="authAside">
        <Link className="brand" href="/"><span className="brandMark">P</span><span>Poyraz Kids</span></Link>
        <div>
          <div className="eyebrow light">EBEVEYN HESABI</div>
          <h1>Güvenli içerik, kontrollü ekran süresi.</h1>
          <p>Hesap erişimi yalnızca ebeveyn veya yasal vasi içindir. Çocuklar için ayrı kullanıcı adı veya şifre oluşturulmaz.</p>
        </div>
        <small>Çocuk verisini minimumda tutuyoruz.</small>
      </section>
      <section className="authCardWrap">
        <form className="authCard">
          <h2>Tekrar hoş geldiniz.</h2>
          <p>Ebeveyn hesabınıza giriş yapın.</p>
          <div className="field"><label>E-posta</label><input type="email" name="email" autoComplete="email" required /></div>
          <div className="field"><label>Şifre</label><input type="password" name="password" autoComplete="current-password" minLength={12} required /></div>
          <button className="primaryButton full" type="submit">Giriş yap</button>
          <p className="formHint">Önerilen güvenlik: en az 12 karakter parola ve hesap ayarlarından iki adımlı doğrulama.</p>
          <p className="formHint">Hesabınız yok mu? <Link href="/register"><b>3 gün ücretsiz deneyin.</b></Link></p>
        </form>
      </section>
    </main>
  );
}
