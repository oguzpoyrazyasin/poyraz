"use server";

import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { developmentGoals } from "@/lib/content";
import { safeChildAge } from "@/lib/security";

const allowedGoals = new Set<string>(developmentGoals);

export async function createChildProfile(formData: FormData) {
  const supabase = await createSupabaseServerClient();
  const { data } = await supabase.auth.getUser();
  if (!data.user) redirect("/login");

  const nickname = String(formData.get("nickname") || "").trim();
  const age = Number(formData.get("age"));
  const goals = formData
    .getAll("goals")
    .map(String)
    .filter(goal => allowedGoals.has(goal))
    .slice(0, 4);

  if (nickname.length < 1 || nickname.length > 30) redirect("/onboarding?error=profile");
  try {
    safeChildAge(age);
  } catch {
    redirect("/onboarding?error=age");
  }

  const { error } = await supabase.from("child_profiles").insert({
    parent_id: data.user.id,
    nickname,
    age,
    goals
  });

  if (error) redirect("/onboarding?error=save");
  redirect("/dashboard");
}
