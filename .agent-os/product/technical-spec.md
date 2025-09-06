# Technical Specification

## Architecture Overview

**Decoupled Enterprise Architecture** implementing provider-agnostic patterns for scalability and vendor flexibility.

### System Flow
```
Contentful App UI → FastAPI Backend → AI Enrichment → Marketing Platform → ActivationLog Evidence
```

## Core Technologies

### Backend Stack
- **FastAPI**: Async Python web framework with automatic OpenAPI docs
- **Pydantic v2**: Schema validation and data contracts 
- **pytest**: Comprehensive testing (23 backend tests)
- **Quality Gates**: Black, Ruff, pre-commit hooks

### Frontend Stack  
- **React + TypeScript**: Type-safe UI development
- **Vite**: Modern build tooling
- **Contentful App SDK**: Direct CMS integration
- **Vitest**: Component testing (7 frontend tests)

### AI Integration
- **OpenAI Provider**: Production GPT models + Vision API (gpt-4o) for image analysis
- **Ollama Provider**: Local models (llama3.2, qwen2.5-coder, deepseek-r1, Qwen 2.5VL 7b)
- **Vision Capabilities**: Automated alt text generation for accessibility compliance
- **Environment Switching**: `AI_PROVIDER=openai|local` configuration

### Marketing Platforms
- **Marketo**: Enterprise marketing automation
- **HubSpot**: Accessible alternative with free tier
- **Mock Service**: Development/testing fallback

## Data Contracts

### Core Schemas
- **ArticleIn**: Validates controlled vocabulary, conditional alt text, CTA fields
- **ActivationPayload**: Ensures outbound data integrity, maps/drops invalid tags
- **ActivationLog**: Captures validation, AI outputs, brand voice analysis

### Controlled Vocabulary
25+ marketing tags across content types, audiences, funnel stages for enterprise governance.

### Brand Voice Analysis
Categorical scoring system for Contentful's brand heuristics:
- Professionalism assessment
- Dual-audience accessibility  
- Action-oriented language detection

## Quality Assurance

### Testing Strategy
- **Unit Tests**: 23 backend + 7 frontend (all passing)
- **Integration Tests**: Mock external API dependencies
- **Schema Validation**: Pydantic ensures data integrity
- **Pre-commit Hooks**: Automated quality gates

### Deployment
- **Docker**: Containerized backend with health checks
- **Render**: One-click cloud deployment via render.yaml
- **Environment**: Configurable providers and platforms

## Audit & Governance

### ActivationLog Structure
```jsonl
{
  "timestamp": "2024-01-01T12:00:00Z",
  "entry_id": "contentful-entry-123",
  "validation_results": {...},
  "ai_enrichment": {...},
  "brand_voice_analysis": {...},
  "marketing_platform_response": {...}
}
```

### Enterprise Features
- **Graceful Degradation**: System continues operation during external service failures
- **Rate Limiting**: Prevents API quota exhaustion
- **Comprehensive Logging**: Every interaction captured for audit
- **Data Contracts**: Pydantic models ensure consistent data shapes