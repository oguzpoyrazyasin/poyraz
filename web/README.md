# Poyraz Kids Web

Professional web platform for the Poyraz Kids 2–6 age product.

## Product model
- Parent/guardian account only
- Child profiles do not have credentials
- 3-day trial
- Starter / Family / Premium subscriptions
- Parent dashboard and child-development activity feed
- PayTR-ready server-side payment layer
- Supabase-ready authentication/database model
- KVKK/privacy-first data minimisation

## Security baseline
- Never store raw card PAN/CVV
- Secrets only in deployment secret store
- TLS-only production
- HttpOnly/Secure/SameSite cookies
- 12+ character passwords; MFA recommended
- Rate limits on auth/payment endpoints
- Parent gate before outbound child-directed content
- Row Level Security for parent-owned records
- Audit subscription/payment webhook events
- No child location, contacts, camera, microphone or exact birthdate by default

## Local run
1. Copy `.env.example` to `.env.local`
2. Add Supabase environment values
3. `npm install`
4. `npm run dev`

## Payment
PayTR merchant credentials must only be configured as deployment secrets. Recurring payments require the corresponding PayTR merchant capabilities/approvals. Implement the callback endpoint and recurring charge worker only after merchant credentials and test environment are available.

## Deployment
Recommended: Replit or another Node hosting provider with managed secrets + PostgreSQL/Supabase. Run `npm run build` before production deployment.
