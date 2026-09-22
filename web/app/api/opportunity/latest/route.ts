/**
 * @file   web/app/api/opportunity/latest/route.ts
 * @brief  Next.js API route that returns the latest ranked opportunities.
 *
 * This endpoint is part of the **Opportunity Router** feature. It provides a
 * lightweight, production‑ready implementation that can be extended later to
 * pull real data from a database or external service.
 *
 * The response shape is deliberately simple so that front‑end components can
 * consume it without additional transformation:
 *
 * 