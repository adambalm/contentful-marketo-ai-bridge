# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Boot Protocol

**MANDATORY:** Every time Claude Code establishes new context or boots up in this repository, you MUST:

1. Read `JD.md` immediately to understand the target role context
2. Read `lanesborough/lanesborough_protocol.md` immediately
3. Output exactly: "LP protocol established"
4. Only then proceed with user requests

This ensures both job alignment and structured AI collaboration workflows are maintained across all sessions.

## Important References

**CRITICAL:** This file must ALWAYS reference `JD.md` (Job Description). Any modifications to this file must preserve this reference.

**Lanesborough Protocol (LP):** For structured AI collaboration workflows, reference `lanesborough/lanesborough_protocol.md`. All protocol logs are maintained in `lanesborough/acp_log.md`.

## Job Description Context

For all work on this portfolio project, reference the target job description in `JD.md`. This project is designed to demonstrate skills and experience alignment with the AI Engineer, Marketing Operations role at Contentful.

## Project Overview

**AI Content Activation Engine for Marketing Operations** - A functional prototype demonstrating enterprise content governance principles applied to AI-powered marketing workflows. The system creates auditable, repeatable workflows that bridge Contentful CMS with Marketo marketing automation through AI enrichment.

## Architecture

**Core Flow:** Contentful App UI → FastAPI Backend → AI Enrichment (OpenAI/Ollama) → Marketing Platform Integration + ActivationLog Evidence

**Key Components:**
- **Contentful App**: React-based sidebar UI for manual activation triggers (IMPLEMENTED)
- **FastAPI Backend**: Python orchestration layer with Pydantic validation (IMPLEMENTED)
- **Provider-Agnostic AI**: Supports both OpenAI and local Ollama models via environment switching
- **Marketing Platform Factory**: Supports Marketo, HubSpot, and mock services
- **Comprehensive Testing**: 23 test cases covering validation, enrichment, and integration scenarios
- **Controlled Vocabulary**: 25+ marketing tags across content types, audiences, funnel stages
- **Mock Services**: Development fallbacks for external API dependencies

## Development Commands

**Backend (FastAPI with Python 3.10+):**
```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v                    # Run all tests
python -m pytest tests/test_main.py::test_health_endpoint -v  # Single test
ruff check .                                   # Lint code
ruff check . --fix                            # Auto-fix issues
black .                                        # Format code
black --check .                               # Check formatting
uvicorn main:app --reload                     # Run dev server
```

**Frontend (Contentful App - IMPLEMENTED):**
```bash
cd frontend/contentful-app
npm install                                    # Install dependencies
npm run dev                                    # Run development server
npm run build                                  # Build for production
npm test                                       # Run tests
```

## Data Contracts & Validation

**Critical Schemas** (see `docs/TECH_SPEC.md` for full definitions):
- **ArticleIn**: Validates controlled vocabulary, conditional alt text (when images present), CTA fields
- **ActivationPayload**: Ensures outbound data integrity, maps/drops invalid tags
- **ActivationLog**: Captures validation results, AI outputs, brand voice analysis for audit/training

**Brand Voice Analysis**: Categorical pass/advisory results for Contentful's brand heuristics (professionalism, dual-audience accessibility, action-oriented language)

## Project Structure

```
portfolio/
├── backend/           # FastAPI application
│   ├── main.py        # Basic FastAPI app with /health endpoint
│   ├── pyproject.toml # Tool configurations (ruff, black, pytest)
│   ├── tests/         # Test suite
│   └── .venv/         # Python virtual environment
├── frontend/          # Contentful App (React-based, implemented)
├── docs/              # Technical documentation
│   ├── PRD.md         # Product Requirements with industry statistics
│   ├── TECH_SPEC.md   # Complete technical specification
│   ├── USER_STORIES.md# Marketing Ops Manager persona
│   └── MVP_ROADMAP.md # 14-day development plan
└── .mcp.json          # MCP servers: memory-bank, github, refs, playwright
```

## MCP Servers Available

- **memory-bank**: Persistent context across sessions (`@movibe/memory-bank-mcp`)
- **github**: Repository operations (`@modelcontextprotocol/server-github`)
- **refs**: Documentation search (`ref-tools-mcp@latest`)
- **playwright**: Browser automation (`@playwright/mcp@latest`)

## Success Metrics & Industry Context

- Reduce content activation cycle: 2-3 days → ≤8 hours
- Address industry gaps: 35% missing meta descriptions, 26% missing alt text, 60-70% unused content
- Target 5.8-30% CTR lift through proper meta description optimization
- 100% controlled vocabulary compliance to prevent poor metadata

## Development Principles

- **Governance-First**: Every AI interaction must be auditable via ActivationLog
- **Enterprise Mindset**: Mock services for external dependencies, graceful degradation
- **Future-Ready**: ActivationLog designed as training data for eventual SFT pipeline
- **Undersell/Overdeliver**: Professional tone, avoid marketing hype, demonstrate actual capabilities

## Critical Security Safeguards

**UTF-16 Surrogate Protection**: All binary data handling MUST use file-first approach to prevent JSON corruption:

```python
# ✅ CORRECT: File-first binary handling
from services.validation_utils import pre_flight_api_validation, validate_file_path_for_binaries

# Validate all API payloads before transmission
pre_flight_api_validation(payload, "api_endpoint_name")

# Use file paths instead of base64 embedding for images
file_path = validate_file_path_for_binaries(image_path)
# Process via file path, not base64 in JSON
```

**NEVER embed binary data in JSON payloads**. This prevents unpaired UTF-16 surrogates that cause API 400 errors and system instability requiring server reboot.

**Implementation**: `backend/services/validation_utils.py` contains comprehensive surrogate detection and prevention utilities with 22 validation tests.

---

*Note: This project aligns with the Contentful AI Engineer, Marketing Operations role requirements. Preserve JD.md reference in all modifications.*
