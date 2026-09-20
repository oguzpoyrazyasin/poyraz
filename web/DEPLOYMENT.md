# Production Deployment Runbook

## Architecture
Browser -> Next.js 16 web app -> Supabase Auth/Postgres
                              -> PayTR hosted payment / callback

Android and Web live in the same GitHub repository but have independent CI pipelines.

## 1. Supabase
Create a production project and run `supabase/schema.sql` in SQL Editor.

Authentication settings:
- Email/password: enabled
- Confirm email: enabled
- Minimum password policy: 12+ characters
- Site URL: production HTTPS domain
- Redirect URLs: production HTTPS domain only (plus explicit staging URL if used)
- MFA TOTP: enable for parents; require for admin accounts when admin UI is added

Copy project values into the hosting provider's encrypted secret store:
- NEXT_PUBLIC_SUPABASE_URL
- NEXT_PUBLIC_SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY

## 2. PayTR
Use the merchant credentials only as encrypted server-side secrets:
- PAYTR_MERCHANT_ID
- PAYTR_MERCHANT_KEY
- PAYTR_MERCHANT_SALT
- PAYTR_TEST_MODE=1 during acceptance, then 0 for production

Configure the PayTR notification/callback URL:
`https://<production-domain>/api/paytr/callback`

Initial billing uses the hosted/iframe payment flow. For unattended renewals, obtain PayTR card-storage + Non3D recurring permissions before enabling a recurring worker.

## 3. Hosting
The app supports standard Node hosting and Docker.

Build:
```bash
cd web
npm install
npm audit --omit=dev --audit-level=high
npm run build
```

Run:
```bash
npm run start
```

Health endpoint:
`GET /api/health`

Docker:
```bash
docker build -t poyraz-kids-web .
docker run --rm -p 3000:3000 --env-file .env.production poyraz-kids-web
```

## 4. Production verification
- HTTPS certificate valid
- /api/health returns ok=true
- Registration requires email confirmation
- Unauthenticated /dashboard, /library, /billing redirect to /login
- First parent account creates a 3-day trial
- Child profile requires only nickname, age, goals
- PayTR test payment callback activates subscription
- Invalid callback HMAC is rejected
- CSP does not block PayTR iframe or Supabase requests
- No secrets appear in browser bundles, logs, source maps, or Git history
- Privacy/terms pages display the final legal entity/contact information

## 5. Commercial launch gates
Before accepting real payments:
- Confirm business/legal entity and invoice process
- Finalize KVKK privacy notice and data-controller contact
- Execute/confirm processor agreements with hosting/auth/payment providers where required
- Confirm PayTR live merchant approval
- Complete trademark/domain clearance for the final product name
- Perform a staging-to-production payment test
