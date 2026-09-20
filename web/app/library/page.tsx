import Link from "next/link";
import { redirect } from "next/navigation";
import { activities } from "@/lib/content";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export const dynamic = "force-dynamic";

export default async function LibraryPage() {
  const supabase = await createSupabaseServerClient();
  const { data } = await supabase.auth.getUser();
  if (!data.user) redirect("/login");

  const { data: child } = await supabase
    .from("child_profiles")
    .select("nickname,age,goals")
    .eq("parent_id", data.user.id)
    .order("created_at", { ascending: true })
    .limit(1)
    .maybeSingle();

  if (!child) redirect("/onboarding");

  const recommended = activities
    .filter(a => a.ages.includes(child.age))
    .sort((a,b) => Number((child.goals || []).includes(b.category)) - Number((child.goals || []).includes(a.category)));

  return (
    <main className="dash">
      <nav className="dashNav">
        <Link className="brand" href="/dashboard"><span className="brandMark">P</span><span>Poyraz Kids</span></Link>
        <Link className="ghostButton" href="/dashboard">Panele dön</Link>
      </nav>
      <div className="dashShell">
        <div className="sectionHead">
          <div className="eyebrow">İÇERİK KÜTÜPHANESİ</div>
          <h2>{child.nickname} için önerilen aktiviteler</h2>
          <p>{child.age} yaş için uygun içerikler; seçtiğiniz gelişim hedefleri üst sıralarda gösterilir.</p>
        </div>
        <div className="libraryGrid">
          {recommended.map(item => (
            <article className="libraryCard" key={item.key}>
              <div className="libraryMeta"><span>{item.category}</span><b>{item.minutes} dk</b></div>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
              <div className="parentTip"><b>Ebeveyn ipucu</b><span>{item.parentTip}</span></div>
              <button className="ghostButton full" type="button">{item.type} • Aktiviteyi aç</button>
            </article>
          ))}
        </div>
      </div>
    </main>
  );
}
