# Poyraz Kids Security Baseline

## Identity
- Parent/guardian accounts only.
- Minimum password length: 12 characters.
- Email verification must be enabled in the production auth provider.
- TOTP MFA should be enabled for parent accounts as an opt-in and required for admin accounts.
- Child profiles never receive credentials.

## Session and authorization
- Server-side auth validation is performed on protected pages and privileged API routes.
- Supabase Row Level Security isolates parent-owned records.
- Subscription/payment state writes use the server-only service role.
- Service-role keys are never exposed with NEXT_PUBLIC_ variables.

## Payments
- Raw card PAN/CVV must never be logged, persisted, proxied, or sent to Supabase.
- PayTR iframe/hosted payment surfaces handle card entry.
- Callback HMAC is verified before subscription state changes.
- Payment events are persisted idempotently.
- Automatic recurring collection must remain disabled until the PayTR account has the required card-storage/Non3D recurring permissions.

## Data minimisation
- Child data: nickname, age (2–6), selected development goals, activity history.
- Do not collect child email, phone, exact birth date, location, photo, contacts, microphone, or camera data by default.
- Avoid behavioral advertising and cross-service tracking.

## HTTP security
Configured globally:
- Content-Security-Policy
- HSTS
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy
- Permissions-Policy

## Secrets
Required production secrets:
- NEXT_PUBLIC_SUPABASE_URL
- NEXT_PUBLIC_SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY
- PAYTR_MERCHANT_ID
- PAYTR_MERCHANT_KEY
- PAYTR_MERCHANT_SALT
- NEXT_PUBLIC_SITE_URL

Never commit real secrets. Rotate any credential that is accidentally exposed.

## CI gates
Production changes must pass:
1. npm audit --omit=dev --audit-level=high
2. npm run build
3. Android CI when shared repository changes affect Android
