import Link from "next/link";
import { plans, TRIAL_DAYS } from "@/lib/plans";

const areas = [
  ["Dil & İletişim", "Kelime, hikâye ve ses oyunlarıyla günlük dil etkileşimini güçlendir."],
  ["Erken Matematik", "Sayı, örüntü, şekil ve karşılaştırmayı oyunlaştırılmış etkinliklerle keşfet."],
  ["Problem Çözme", "Eşleştirme, sıralama ve neden-sonuç aktiviteleriyle düşünme becerilerini destekle."],
  ["Motor Gelişim", "Ekranla sınırlı kalmayan hareket, denge ve ince motor görevleriyle aktif öğren."],
  ["Yaratıcılık", "Müzik, çizim, hikâye kurma ve açık uçlu oyunlarla üretkenliği teşvik et."],
  ["Merak & Bilim", "Günlük hayattan basit deneyler ve 'neden?' sorularıyla keşfetme alışkanlığı kazandır."]
];

export default function HomePage() {
  return (
    <main>
      <nav className="nav shell">
        <Link className="brand" href="/">
          <span className="brandMark">P</span>
          <span>Poyraz Kids</span>
        </Link>
        <div className="navLinks">
          <a href="#nasil">Nasıl çalışır?</a>
          <a href="#gelisim">Gelişim alanları</a>
          <a href="#fiyat">Fiyatlandırma</a>
          <Link className="ghostButton" href="/login">Giriş yap</Link>
          <Link className="primaryButton small" href="/register">{TRIAL_DAYS} gün ücretsiz dene</Link>
        </div>
      </nav>

      <section className="hero shell">
        <div className="heroCopy">
          <div className="eyebrow">2–6 YAŞ • EBEVEYN KONTROLLÜ • REKLAMSIZ</div>
          <h1>Çocuğunuz için ekrandan fazlasını sunan akıllı gelişim platformu.</h1>
          <p className="lead">
            Yaşa uygun oyunları, eğitim videolarını ve gerçek dünya aktivitelerini tek bir güvenli akışta birleştirir.
            Ebeveyn olarak ne izlendiğini, ne oynandığını ve hangi gelişim alanının desteklendiğini siz yönetirsiniz.
          </p>
          <div className="heroActions">
            <Link className="primaryButton" href="/register">{TRIAL_DAYS} gün ücretsiz başla</Link>
            <a className="textButton" href="#nasil">Platformu keşfet →</a>
          </div>
          <div className="trustRow">
            <span>✓ Çocuk hesabı yok</span>
            <span>✓ Kart verisi bizde tutulmaz</span>
            <span>✓ İstediğiniz zaman iptal</span>
          </div>
        </div>

        <div className="heroVisual">
          <div className="orb orbOne" />
          <div className="orb orbTwo" />
          <div className="phoneCard">
            <div className="miniTop"><span>Bugünün planı</span><b>18 dk</b></div>
            <div className="activity purple">
              <div><small>3–4 YAŞ • DİL</small><strong>Hikâyeyi Tamamla</strong></div><span>▶</span>
            </div>
            <div className="activity yellow">
              <div><small>ERKEN MATEMATİK</small><strong>Şekil Avı</strong></div><span>◆</span>
            </div>
            <div className="activity green">
              <div><small>EKRAN DIŞI</small><strong>Hareket Molası</strong></div><span>↗</span>
            </div>
            <div className="progressCard">
              <div><strong>Bu hafta</strong><span>4 / 5 gün</span></div>
              <div className="bar"><i /></div>
            </div>
          </div>
        </div>
      </section>

      <section className="stats">
        <div className="shell statsGrid">
          <div><b>2–6</b><span>yaşa özel akış</span></div>
          <div><b>6</b><span>gelişim alanı</span></div>
          <div><b>3 gün</b><span>ücretsiz deneme</span></div>
          <div><b>0 reklam</b><span>odak çocukta</span></div>
        </div>
      </section>

      <section id="nasil" className="section shell">
        <div className="sectionHead">
          <div className="eyebrow">NASIL ÇALIŞIR?</div>
          <h2>Ebeveyn kontrolünde, basit ve sürdürülebilir.</h2>
          <p>Platform çocuğu ekrana bağlamak için değil, kaliteli içeriği doğru dozda kullanmak için tasarlanır.</p>
        </div>
        <div className="steps">
          {[
            ["01", "Ebeveyn hesabını oluştur", "Hesabı yalnızca yetişkin açar. Çocuk için isim yerine takma ad ve yaş grubu yeterlidir."],
            ["02", "Yaşı ve hedefleri seç", "Dil, matematik, problem çözme, motor gelişim ve yaratıcılık alanlarından öncelikleri belirle."],
            ["03", "Günlük akışı kullan", "Kısa dijital içerik + ebeveyn etkileşimi + ekran dışı aktivite dengesiyle ilerle."],
            ["04", "İlerlemeyi takip et", "Haftalık kullanım özeti ve gelişim alanı dağılımını ebeveyn panelinden gör."]
          ].map(([n, t, d]) => (
            <article className="step" key={n}>
              <span>{n}</span><h3>{t}</h3><p>{d}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="gelisim" className="section soft">
        <div className="shell">
          <div className="sectionHead">
            <div className="eyebrow">GELİŞİM ALANLARI</div>
            <h2>Her aktivitenin bir amacı var.</h2>
          </div>
          <div className="areaGrid">
            {areas.map(([title, desc], i) => (
              <article className="areaCard" key={title}>
                <span className="areaIcon">{["Aa","12","?","↟","✦","⚗"][i]}</span>
                <h3>{title}</h3><p>{desc}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="fiyat" className="section shell">
        <div className="sectionHead center">
          <div className="eyebrow">FİYATLANDIRMA</div>
          <h2>Önce deneyin. Sonra size uygun planı seçin.</h2>
          <p>Tüm planlarda ilk {TRIAL_DAYS} gün ücretsiz. Deneme süresinde ücret alınmaz.</p>
        </div>
        <div className="pricingGrid">
          {plans.map((plan) => (
            <article className={`priceCard ${plan.highlighted ? "featured" : ""}`} key={plan.id}>
              {plan.highlighted && <div className="badge">En çok tercih edilen</div>}
              <h3>{plan.name}</h3>
              <div className="price"><b>₺{plan.monthlyPriceTry}</b><span>/ ay</span></div>
              <p>veya yıllık ₺{plan.annualPriceTry}</p>
              <ul>{plan.features.map((f) => <li key={f}>✓ {f}</li>)}</ul>
              <Link className={plan.highlighted ? "primaryButton full" : "ghostButton full"} href={`/register?plan=${plan.id}`}>
                {TRIAL_DAYS} gün ücretsiz başla
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section className="cta">
        <div className="shell ctaInner">
          <div>
            <div className="eyebrow light">POYRAZ KIDS</div>
            <h2>Çocukların merakını doğru içerikle büyütün.</h2>
            <p>Bir hesap oluşturun, yaş grubunu seçin ve ilk planınızı dakikalar içinde hazırlayın.</p>
          </div>
          <Link className="whiteButton" href="/register">Ücretsiz denemeyi başlat</Link>
        </div>
      </section>

      <footer className="footer shell">
        <div><b>Poyraz Kids</b><p>2–6 yaş çocuk gelişimi için ebeveyn kontrollü dijital platform.</p></div>
        <div className="footerLinks">
          <Link href="/legal/privacy">Gizlilik</Link>
          <Link href="/legal/terms">Kullanım Koşulları</Link>
          <a href="mailto:hello@poyrazkids.com">İletişim</a>
        </div>
        <small>© 2026 Poyraz Kids. Tüm hakları saklıdır.</small>
      </footer>
    </main>
  );
}
