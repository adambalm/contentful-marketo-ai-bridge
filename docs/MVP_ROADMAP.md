# Artifact 1 · Master Project Checklist (Merged 14-Day Sprint)

> Scope: **Phase 1 (MVP)** — Contentful App (manual trigger) → FastAPI → Marketo  
> Repo structure assumed: monorepo with `/backend` (FastAPI) and `/frontend/contentful-app` (Contentful App).  
> Prereqs: Root `.env.template`, root `README.md`, Contentful sandbox space.

---

## Phase 1: Foundations & Backend Core (Days 1–5)

### Day 1: Project & Sandbox Setup
- [ ] Apply for **Marketo Developer Sandbox** (note lead time).
- [ ] Create public GitHub repository (root: `portfolio/`).
- [ ] Add root **`.env.template`** (Contentful, Marketo, OpenAI placeholders).
- [ ] Create `/docs/` and seed artifacts (this file + user stories + diagram).
- [ ] Draft initial **`README.md`** skeleton (problem → solution → demo → setup).

### Day 2: Backend Foundation & Quality Tools
- [ ] In `/backend`, create Python venv and **FastAPI** scaffold (`main.py`, `requirements.txt`, `pyproject.toml`).
- [ ] Configure **pytest**; add health-check test in `/backend/tests/test_main.py`.
- [ ] Configure **ruff** + **black** in `pyproject.toml`.
- [ ] Commit: `feat(backend): initialize FastAPI and code quality tooling`.

### Day 3: Frontend Foundation & Contentful Models
- [ ] In `/frontend`, scaffold Contentful App:  
  `npx create-contentful-app contentful-app`
- [ ] Add **eslint** + **prettier** to `/frontend/contentful-app`.
- [ ] In Contentful, create models:
  - **Article** (title, summary, body, tags, status)
  - **ActivationLog** (article ref, timestamp, actions[], evidence JSON, status)

### Day 4: Pydantic Contracts & API Endpoint
- [ ] In `/backend`, define Pydantic models:
  - `ArticleIn` (incoming Contentful data)
  - `ActivationPayload` (outbound to Marketo)
- [ ] Build `/activate` FastAPI endpoint: accept `ArticleIn` → validate → return 200 with stub payload.
- [ ] Add pytest for validation (happy path + failure cases).

### Day 5: AI Enrichment & Evidence Logging
- [ ] Integrate OpenAI client in `/backend/services/ai_service.py`.
- [ ] Enrichment in `/activate`: generate `summary` (≤160 chars), `keywords` (3–7).
- [ ] Integrate Contentful **Management API** client.
- [ ] MVP logging: write **ActivationLog** entry (evidence JSON) back to Contentful.

---

## Phase 2: Integration & Showcase (Days 6–14)

### Days 6–7: Marketo Integration (or Mock)
- [ ] Implement `/backend/services/marketo_service.py` (auth, add-to-list).
- [ ] From `/activate`, push `ActivationPayload` to Marketo list.
- [ ] If sandbox not approved: enable **mock Marketo API** (logs payload + 200).

### Days 8–9: Contentful App UI
- [ ] Build minimal **sidebar** UI (React):
  - Button: **"Activate in Marketo"**
  - Status area: last activation result + link to ActivationLog
- [ ] Wire button → FastAPI `/activate`.
- [ ] Display latest **ActivationLog** (via Contentful CDA or Mgmt API).

### Days 10–11: End-to-End Testing & Refinement
- [ ] Run full flow: App → Backend → (Marketo or mock) → Log back.
- [ ] Improve error handling, toasts, and loading states.

### Days 12–14: The Showcase
- [ ] Finalize `README.md` narrative (governance → marketing velocity).
- [ ] Embed Mermaid **architecture diagram**.
- [ ] Record and embed **demo GIF** (App trigger + logs).
- [ ] Deploy `/backend` to **Render**; expose URL in README.
- [ ] Clean repo; ensure red/green contract checks and instructions are clear.

---

## Deliverables for Phase 1
- Running Contentful App (manual trigger), FastAPI, and Marketo (or mock).
- Evidence logging into Contentful.
- README with demo GIF, diagram, setup, and narrative.
- This checklist + user stories + diagram in `/docs/`.

## Notes & Risks
- **Marketo sandbox** can delay; keep mock ready.
- Keep **AI outputs advisory**; Pydantic validations are authoritative.
- Treat **Contentful App** as the portfolio "face"; polish the UX.