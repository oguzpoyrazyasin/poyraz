"use server";

import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";

const allowedPlans = new Set(["starter", "family", "premium"]);

function cleanEmail(value: FormDataEntryValue | null) {
  return String(value || "").trim().toLowerCase();
}

export async function signUp(formData: FormData) {
  const name = String(formData.get("name") || "").trim();
  const email = cleanEmail(formData.get("email"));
  const password = String(formData.get("password") || "");
  const requestedPlan = String(formData.get("plan") || "family");
  const plan = allowedPlans.has(requestedPlan) ? requestedPlan : "family";

  if (name.length < 2 || !email.includes("@") || password.length < 12) {
    redirect("/register?error=invalid");
  }

  const supabase = await createSupabaseServerClient();
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        full_name: name,
        plan_id: plan,
        account_type: "parent"
      }
    }
  });

  if (error) redirect("/register?error=signup");

  if (data.session) redirect("/dashboard");
  redirect("/login?message=verify-email");
}

export async function signIn(formData: FormData) {
  const email = cleanEmail(formData.get("email"));
  const password = String(formData.get("password") || "");

  const supabase = await createSupabaseServerClient();
  const { error } = await supabase.auth.signInWithPassword({ email, password });

  if (error) redirect("/login?error=invalid-credentials");
  redirect("/dashboard");
}

export async function signOut() {
  const supabase = await createSupabaseServerClient();
  await supabase.auth.signOut();
  redirect("/");
}
