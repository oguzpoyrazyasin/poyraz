export const securityPolicy = {
  accountOwner: "parent_or_guardian_only",
  childLogin: false,
  minimumPasswordLength: 12,
  recommendedMfa: "totp",
  sessionPolicy: "httpOnly_secure_sameSite_lax",
  paymentCardStorage: "payment_provider_only",
  childDataPrinciple: "data_minimisation"
} as const;

export function safeChildAge(age: number) {
  if (!Number.isInteger(age) || age < 2 || age > 6) {
    throw new Error("Çocuk yaşı 2 ile 6 arasında olmalıdır.");
  }
  return age;
}
