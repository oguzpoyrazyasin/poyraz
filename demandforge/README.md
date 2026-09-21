# DemandForge MVP

DemandForge is an AI-native **Demand-to-Factory Commerce OS** prototype. It converts customer intent into a structured Product Genome, scores candidate suppliers, models landed cost, produces Pareto commercial options, drafts RFQs and keeps high-impact commercial actions approval-gated.

## Current MVP capabilities

- Natural-language intent → Product Genome
- Seeded China supplier intelligence
- Weighted supplier risk scoring with hard-gate support
- Landed-cost decomposition
- Budget / Balanced / Premium commercial scenarios
- Mock RFQ dispatch
- Approval threshold endpoint
- Agent control-plane metadata
- Audit event capture
- Responsive B2B SaaS UI

## Run locally

1. Install Node.js 20+
2. `npm install`
3. `npm run dev`
4. Open `http://localhost:5173`

API runs on port `8787`.

## Safety boundary

The MVP intentionally does **not** execute real purchase orders, payments, advertising spend, binding supplier acceptance, or bank transfers. RFQ delivery is mocked. Production integrations must route high-impact actions through the approval policy engine.

## Target production architecture

Frontend: React / Next.js  
API: Node/NestJS or equivalent typed service layer  
AI services: Python/FastAPI  
Workflow: Temporal  
Transaction DB: PostgreSQL  
Semantic retrieval: pgvector  
Cache: Redis  
Events: Kafka/Redpanda at scale  
Documents: S3-compatible object storage  
Observability: OpenTelemetry

## Primary entities

User, Organization, Intent, ProductSpec, Supplier, SupplierCapability, SupplierDocument, RFQ, Quote, QuoteLine, LogisticsQuote, ComplianceCheck, CommercialOption, Approval, PurchaseOrder, Order, Shipment, Payment, QCInspection, Return, AgentRun, AuditEvent.

## Production hardening checklist

- Real authentication and organization tenancy
- Database migrations and row-level access controls
- Supplier connector authorization and ToS review
- Sanctions and beneficiary screening
- EU/US compliance rule versioning
- Idempotency keys on every commercial mutation
- Human approval policies
- Secrets management / KMS
- Signed webhook validation
- Evidence-backed compliance records
- Deterministic workflow state machine
- Rate limiting and anti-abuse controls
- Continuous audit logs
- Contract/legal review before real supplier execution

## Branch

This MVP is intentionally isolated on `demandforge-mvp` so the repository's default branch is unchanged.
