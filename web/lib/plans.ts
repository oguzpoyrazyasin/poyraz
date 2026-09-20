export type PlanId = "starter" | "family" | "premium";

export type Plan = {
  id: PlanId;
  name: string;
  monthlyPriceTry: number;
  annualPriceTry: number;
  childLimit: number;
  features: string[];
  highlighted?: boolean;
};

export const TRIAL_DAYS = 3;

export const plans: Plan[] = [
  {
    id: "starter",
    name: "Başlangıç",
    monthlyPriceTry: 149,
    annualPriceTry: 1490,
    childLimit: 1,
    features: [
      "1 çocuk profili",
      "Yaşa göre akıllı oyun ve video akışı",
      "Haftalık aktivite önerileri",
      "Ebeveyn ilerleme özeti"
    ]
  },
  {
    id: "family",
    name: "Aile",
    monthlyPriceTry: 249,
    annualPriceTry: 2490,
    childLimit: 3,
    highlighted: true,
    features: [
      "3 çocuk profiline kadar",
      "Tüm gelişim kategorileri",
      "Kişiselleştirilmiş haftalık plan",
      "Gelişim alanı bazlı ilerleme paneli",
      "Favoriler ve aktivite geçmişi"
    ]
  },
  {
    id: "premium",
    name: "Premium",
    monthlyPriceTry: 399,
    annualPriceTry: 3990,
    childLimit: 5,
    features: [
      "5 çocuk profiline kadar",
      "Aile planındaki tüm özellikler",
      "Detaylı aylık gelişim raporu",
      "Yeni içeriklere erken erişim",
      "Öncelikli destek"
    ]
  }
];

export function trialEndsAt(start = new Date()) {
  const d = new Date(start);
  d.setDate(d.getDate() + TRIAL_DAYS);
  return d;
}
