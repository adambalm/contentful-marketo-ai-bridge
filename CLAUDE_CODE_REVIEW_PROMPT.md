# Claude Code Review Prompt: Contentful-Marketo-AI-Bridge Project Status

## Context
I need you to review the current state of this Contentful-Marketo-AI-Bridge project and provide a baseline reset report. I'm experiencing confusion about what's actually running, where, and what gaps exist between the current implementation and the MVP roadmap.

## What I Believe to Be True (Please Verify/Correct)

### Project Structure
- **Repository**: `/home/ed/contentful-marketo-ai-bridge/` on a Linux server
- **Backend**: FastAPI app in `/backend/` with Python virtual environment at `.venv/`
- **Frontend**: Contentful App in `/frontend/contentful-app/` (React/TypeScript)
- **User Environment**: Mac connecting remotely to Linux server via Cursor IDE

### Current Running Services (From `ss -tulpn` output)
- **Port 8010**: Our backend (uvicorn) - `main:app --host 127.0.0.1 --port 8010`
- **Port 3000**: Open WebUI Docker container (AI chat interface)
- **Port 8000**: Portainer Docker container (Docker management)
- **Port 11434**: Ollama (local AI provider)
- **Multiple Node.js processes**: Cursor IDE services and MCP tools

### Recent Implementation Changes
- Added brand-voice advisory mapping to backend
- Added rate limiting (10 req/min) to `/activate` endpoint
- Added `GET /activation-log/{entry_id}` endpoint
- Updated Sidebar to display brand-voice advisories
- Backend tests: 23/23 passing
- Frontend tests: 7/7 passing

### MVP Roadmap Status (From docs/MVP_ROADMAP.md)
**Phase 1: Foundations & Backend Core (Days 1–5)**
- [x] FastAPI scaffold
- [x] Pydantic schemas (ArticleIn, ActivationResult)
- [x] Tests and code quality tools
- [x] AI enrichment service (OpenAI + local provider)
- [x] Mock Contentful service
- [x] Mock Marketo service
- [x] Basic activation endpoint

**Phase 2: Integration & Showcase (Days 6–14)**
- [x] Contentful App UI scaffold
- [x] Sidebar with "Activate in Marketo" button
- [x] Mock Marketo integration
- [ ] **GAP**: Contentful App installation and content type setup
- [ ] **GAP**: End-to-end testing in actual Contentful environment
- [ ] **GAP**: Demo GIF and README showcase
- [ ] **GAP**: Render deployment

## Critical Questions for Review

### 1. Architecture & Deployment
- Is the backend actually accessible from external clients (Mac) or only localhost?
- Should the Contentful App run on the Mac or the Linux server?
- What's the correct network configuration for testing?

### 2. Contentful Integration
- Do we have actual Contentful space setup with Article/ActivationLog content types?
- Is the Contentful App actually installed and configured?
- What's the difference between `npm run dev` vs `npm start` for Contentful Apps?

### 3. Testing Workflow
- How do we actually test the full user workflow (Contentful → Backend → Marketo)?
- What's the correct sequence to see the sidebar in action?
- Are we missing any environment variables or configuration?

### 4. MVP Completion
- What specific steps remain to complete the MVP roadmap?
- What's the minimum viable setup to demonstrate the full flow?
- What are the critical gaps preventing end-to-end testing?

## Requested Output

Please provide a **Baseline Reset Report** that includes:

1. **Current State Verification**: Confirm or correct my understanding of what's running where
2. **Gap Analysis**: Specific gaps between current state and MVP completion
3. **Next Steps**: Prioritized list of exactly what must be done next
4. **Testing Plan**: Step-by-step instructions to see the full flow in action
5. **Environment Setup**: Required configurations, environment variables, and network setup
6. **Success Criteria**: How we'll know when the MVP is complete and working

## Files to Review
- `/docs/MVP_ROADMAP.md` - Original roadmap
- `/docs/PRD.md` - Product requirements
- `/docs/TECH_SPEC.md` - Technical specifications
- `/backend/main.py` - Current backend implementation
- `/frontend/contentful-app/src/locations/Sidebar.tsx` - Current frontend
- `/README.md` - Current project status

Please be specific about network configuration, Contentful setup requirements, and the exact sequence needed to test the complete user workflow.
