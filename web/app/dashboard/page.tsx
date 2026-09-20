import Link from "next/link";

export default function DashboardPage() {
  return (
    <main className="dash">
      <nav className="dashNav">
        <Link className="brand" href="/"><span className="brandMark">P</span><span>Poyraz Kids</span></Link>
        <Link className="ghostButton" href="/">Çıkış</Link>
      </nav>
      <div className="dashShell">
        <div className="welcome">
          <div><h1>Günaydın 👋</h1><p>Bugünün kısa ve dengeli gelişim planı hazır.</p></div>
          <span className="trialPill">Ücretsiz deneme • 2 gün kaldı</span>
        </div>
        <div className="dashGrid">
          <section className="panel">
            <h3>Bugünün aktiviteleri</h3>
            <div className="miniActivities">
              <div className="miniActivity"><div><b>Hikâyeyi Tamamla</b><br/><small>Dil • 8 dakika</small></div><span>▶</span></div>
              <div className="miniActivity"><div><b>Şekil Avı</b><br/><small>Erken Matematik • 7 dakika</small></div><span>◆</span></div>
              <div className="miniActivity"><div><b>Hareket Molası</b><br/><small>Kaba Motor • ekran dışı</small></div><span>↗</span></div>
            </div>
          </section>
          <aside className="panel">
            <h3>Bu hafta</h3>
            <p><b>4 / 5 gün</b> plan tamamlandı.</p>
            <div className="bar"><i /></div>
            <p className="formHint">En çok çalışılan alan: Dil & İletişim</p>
          </aside>
        </div>
      </div>
    </main>
  );
}
