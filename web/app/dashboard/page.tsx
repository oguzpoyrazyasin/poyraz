import Link from "next/link";
import { redirect } from "next/navigation";
import { signOut } from "@/app/auth/actions";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

function remainingDays(endsAt?: string | null) {
  if (!endsAt) return 0;
  const ms = new Date(endsAt).getTime() - Date.now();
  return Math.max(0, Math.ceil(ms / 86400000));
}

export default async function DashboardPage() {
  const supabase = await createSupabaseServerClient();
  const { data: authData } = await supabase.auth.getUser();
  if (!authData.user) redirect("/login");

  const [{ data: profile }, { data: subscription }, { count: childCount }] = await Promise.all([
    supabase.from("profiles").select("full_name").eq("id", authData.user.id).maybeSingle(),
    supabase.from("subscriptions")
      .select("plan_id,status,trial_ends_at,current_period_end")
      .eq("parent_id", authData.user.id)
      .order("created_at", { ascending: false })
      .limit(1)
      .maybeSingle(),
    supabase.from("child_profiles")
      .select("id", { count: "exact", head: true })
      .eq("parent_id", authData.user.id)
  ]);

  if ((childCount || 0) === 0) redirect("/onboarding");

  const days = remainingDays(subscription?.trial_ends_at);
  const trialing = subscription?.status === "trialing";

  return (
    <main className="dash">
      <nav className="dashNav">
        <Link className="brand" href="/"><span className="brandMark">P</span><span>Poyraz Kids</span></Link>
        <div className="dashActions">
          <Link className="ghostButton" href="/library">İçerik kütüphanesi</Link>
          <form action={signOut}><button className="ghostButton" type="submit">Çıkış</button></form>
        </div>
      </nav>
      <div className="dashShell">
        <div className="welcome">
          <div><h1>Merhaba {profile?.full_name?.split(" ")[0] || "👋"}</h1><p>Bugünün kısa ve dengeli gelişim planı hazır.</p></div>
          {trialing ? (
            <span className="trialPill">Ücretsiz deneme • {days} gün kaldı</span>
          ) : (
            <span className="trialPill">{subscription?.plan_id || "Plan"} • {subscription?.status || "hazırlanıyor"}</span>
          )}
        </div>
        <div className="dashGrid">
          <section className="panel">
            <h3>Bugünün aktiviteleri</h3>
            <div className="miniActivities">
              <div className="miniActivity"><div><b>Hikâyeyi Tamamla</b><br/><small>Dil • 8 dakika</small></div><span>▶</span></div>
              <div className="miniActivity"><div><b>Şekil Avı</b><br/><small>Erken Matematik • 7 dakika</small></div><span>◆</span></div>
              <div className="miniActivity"><div><b>Hareket Molası</b><br/><small>Kaba Motor • ekran dışı</small></div><span>↗</span></div>
            </div>
            <div className="panelAction">
              <Link href="/library" className="primaryButton">Tüm önerileri aç</Link>
            </div>
          </section>
          <aside className="panel">
            <h3>Üyelik</h3>
            <p><b>{subscription?.plan_id || "Family"}</b> planı</p>
            <p className="formHint">{trialing ? "Deneme sonunda ücret alınmaz; devam etmek için ödeme onayı gerekir." : "Abonelik durumunuzu hesap bölümünden yönetebilirsiniz."}</p>
            <Link href="/billing" className="primaryButton full">Planı ve ödemeyi yönet</Link>
          </aside>
        </div>
      </div>
    </main>
  );
}
