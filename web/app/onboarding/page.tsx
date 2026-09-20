import Link from "next/link";
import { redirect } from "next/navigation";
import { createChildProfile } from "@/app/children/actions";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { developmentGoals } from "@/lib/content";

export const dynamic = "force-dynamic";

export default async function OnboardingPage() {
  const supabase = await createSupabaseServerClient();
  const { data } = await supabase.auth.getUser();
  if (!data.user) redirect("/login");

  const { count } = await supabase
    .from("child_profiles")
    .select("id", { count: "exact", head: true })
    .eq("parent_id", data.user.id);

  if ((count || 0) > 0) redirect("/dashboard");

  return (
    <main className="authPage">
      <section className="authAside">
        <Link className="brand" href="/"><span className="brandMark">P</span><span>Poyraz Kids</span></Link>
        <div>
          <div className="eyebrow light">ÇOCUK PROFİLİ</div>
          <h1>Gerektiği kadar bilgi. Daha fazlası değil.</h1>
          <p>Çocuğunuz için yalnızca takma ad, yaş ve gelişim hedefleri yeterli. Tam doğum tarihi, e-posta, telefon veya fotoğraf istemiyoruz.</p>
        </div>
        <small>Profil yalnızca ebeveyn hesabınızdan yönetilir.</small>
      </section>
      <section className="authCardWrap">
        <form className="authCard" action={createChildProfile}>
          <h2>İlk profili oluşturun.</h2>
          <p>Önerileri yaşa ve hedeflere göre kişiselleştireceğiz.</p>
          <div className="field"><label>Takma ad</label><input name="nickname" maxLength={30} required placeholder="Örn. Minik Kaşif" /></div>
          <div className="field">
            <label>Yaş</label>
            <select name="age" defaultValue="3">{[2,3,4,5,6].map(age => <option key={age} value={age}>{age} yaş</option>)}</select>
          </div>
          <fieldset className="goalSet">
            <legend>Öncelikli gelişim alanları (en fazla 4)</legend>
            {developmentGoals.map(goal => (
              <label key={goal} className="goalOption">
                <input type="checkbox" name="goals" value={goal} />
                <span>{goal}</span>
              </label>
            ))}
          </fieldset>
          <button className="primaryButton full" type="submit">Profili oluştur ve başla</button>
        </form>
      </section>
    </main>
  );
}
