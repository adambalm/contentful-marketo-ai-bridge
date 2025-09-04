# Product Requirements Document (PRD)
## Project: Marketing Activation Engine

### Problem Statement
Contentful is strong at content modeling, entry management, APIs, and basic webhooks. But it does not provide:
- Semantic validation beyond field type checks.
- Automated enrichment (summaries, SEO tags, tone checks).
- Direct integration with marketing automation platforms (e.g., Marketo).
- An auditable trail of *why* content was enriched, tagged, or approved.

As a result, Marketing Ops teams spend time manually tagging, copying, and validating content before it can be used in campaigns. This creates 2-3 day content-to-campaign cycles, introduces inconsistency, and makes it difficult to integrate with existing marketing operations workflows or audit AI involvement.

### Goals
- Reduce content-to-campaign activation cycle from days to hours through automated workflows.
- Use AI to enrich and check content, filling the gaps Contentful does not natively solve.  
- Enable cross-functional collaboration between Marketing, RevOps, and Engineering teams.
- Log every enrichment and decision inside Contentful for transparency.  
- Deliver a minimal, working MVP with clear extensibility for future orchestration.

### Target User
- **Marketing Operations Manager ("Maria")**, responsible for getting campaign assets live quickly and correctly.

### User Stories (summarized)
1. Maria wants to avoid manual tagging so campaigns launch faster and stay consistent.  
2. Maria wants AI to check brand voice consistency before campaign activation.  
3. Maria wants an audit trail of AI-generated suggestions and approvals.  

(See `/docs/USER_STORIES.md` for detailed stories.)

### Success Metrics
- Reduce content-to-campaign activation cycle from 2–3 days → same-day (≤8 hours).
- Ensure 100% of activated entries include meta descriptions; industry data shows ~35% of sites miss them and ~50% use duplicates.
- Increase CTR potential: properly sized/designed meta descriptions can yield 5.8–30% more clicks.
- Guarantee every activation is tagged with controlled vocab, reducing the 60–70% unused content rate tied to poor metadata.
- Every activated asset generates an ActivationLog, providing evidence of AI outputs and validation results for audit purposes.

---

### Technology Approach

The project uses Contentful as the system of record and adds external components where Contentful does not provide capabilities.

**1. Pydantic (Backend Data Validation)**  
- **Problem:** Contentful only enforces types (string, integer, reference). It does not enforce semantic rules (e.g., "title must be ≤ 70 characters").  
- **Solution:** Define strict Pydantic models in Python to validate incoming entries:
  - `ArticleIn` schema: enforces field presence, title length, controlled vocabulary for campaign_tags, alt text completeness.  
  - `ActivationPayload` schema: ensures the outbound Marketo payload is well-formed.  
- **Value:** Prevents "garbage in" and enforces marketing-specific rules Contentful cannot.

**2. FastAPI (Backend Orchestration)**  
- **Problem:** Contentful webhooks and App buttons can call external services, but they cannot orchestrate multi-step logic.  
- **Solution:** Use FastAPI as a backend service:
  - Expose `/activate` endpoint triggered by Contentful App button.  
  - Chain validation → AI enrichment → Marketo push → evidence logging.  
- **Value:** Provides a single orchestration layer and future extensibility for branching workflows.

**3. OpenAI (AI Enrichment & Brand Voice Analysis)**  
- **Problem:** Contentful does not generate summaries, keywords, or evaluate brand consistency.  
- **Solution:** OpenAI generates:
  - Meta description for SEO (≤160 chars).  
  - Suggested keyword list (3–7 items).  
  - Brand voice analysis using Contentful's brand heuristics: professionalism (aspirational, forward-thinking, technically credible), dual-audience accessibility (technical depth + empowering simplicity), action-oriented language (active verbs, efficiency metaphors).  
- **Value:** Automates manual enrichment, ensures brand consistency, speeds campaign readiness. Brand voice outputs are advisory-only and never block activation in MVP.

**4. Contentful App (UI Trigger & Display)**  
- **Problem:** Content editors need a simple interface to initiate activation and view logs.  
- **Solution:** A sidebar app provides:
  - "Activate in Marketo" button that calls FastAPI.  
  - Status display showing the latest ActivationLog.  
- **Value:** Keeps the workflow inside Contentful, accessible to non-technical users.

**5. Contentful Management API (Evidence Logging)**  
- **Problem:** Contentful logs entry changes but not the *reasoning* behind AI enrichment.  
- **Solution:** A custom content type (`ActivationLog`) stores:
  - Original AI outputs (summary, keywords, tone check).  
  - Validation results.  
  - Status (`draft`, `pending_review`, `pushed`).  
- **Value:** Creates an audit trail visible in the same system where content lives.

**6. Marketo API Connector**  
- **Problem:** Contentful cannot push assets directly into Marketo for list membership updates.  
- **Solution:** Custom Python connector (`marketo_service.py`) handles:
  - Authentication to Marketo sandbox.  
  - List membership updates only (campaign creation and lead management are future scope).  
  - Mock service fallback if sandbox is unavailable.  
- **Value:** Bridges CMS → marketing automation gap for essential list operations.

**7. Extensibility Hooks (Future: LangGraph & MCP)**  
- **Problem:** Linear workflows are brittle for retries, escalation, or multi-agent orchestration. Contentful has no solution here.  
- **Future Solution:**  
  - **LangGraph:** Replace linear FastAPI orchestration with a stateful graph that can branch, retry, or pause for human approval.  
  - **MCP (Model Context Protocol):** Provide a standardized way for multiple LLMs (OpenAI, Claude, Vertex) to access Contentful and Marketo as "tools," instead of custom glue code.  
- **Value:** Ensures system design remains flexible and future-ready without committing to complexity at MVP stage.

---

### Phases
- **Phase 1 (MVP):**  
  - Contentful App button triggers `/activate`.  
  - FastAPI validates with Pydantic, enriches with OpenAI, pushes to Marketo, and logs to Contentful.  
  - Evidence visible in ActivationLog.  

- **Phase 2 (Vision):**  
  - Webhook-driven automation instead of manual button click.  
  - Multi-variant generation for personalization.  

- **Phase 3 (Vision):**  
  - Strategic dashboards aggregating ActivationLogs to show ROI, velocity, and quality metrics.  

---

### Out of Scope (MVP)
- Custom analytics dashboards.  
- Multi-agent orchestration (LangGraph, MCP).  
- Production Marketo account (sandbox or mock only).
- Campaign creation, lead scoring, multi-asset types (beyond Article).  

---

### Risks
- Without validation/enrichment, entries risk falling into the 35% of pages with missing metadata and 60–70% of unused content buckets.
- Missing alt text (present in only 26% of sites) undermines accessibility and SEO.
- Marketo sandbox delays may stall real integrations; mitigated by mock connector.
- AI outputs may be inconsistent; mitigated by schema validation + human-in-the-loop review.
- Change management: team adoption may lag without clear governance and training.

---