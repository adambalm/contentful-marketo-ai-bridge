# System Dependency Map

## Overview

This document maps the critical dependencies in the AI Content Activation Engine, highlighting what's implemented vs. what's blocking progress toward a working demo.

## Core Workflow Dependencies

### Main Activation Pipeline
```
/activate endpoint (main.py:70-199)
    ├── 1. Content Retrieval
    │   └── ContentfulService.get_article()          [🔴 MOCK - CRITICAL BLOCKER]
    │       ├── Real Implementation: contentful SDK   [❌ Not installed]
    │       ├── Content Model Setup: Space + Tokens   [❌ Missing]
    │       └── Field Mapping: Contentful → Pydantic [❌ Not implemented]
    │
    ├── 2. Content Validation  
    │   └── ArticleIn.validate()                     [🟢 COMPLETE]
    │       ├── Controlled Vocabulary: 25+ tags      [✅ Working]
    │       ├── Alt Text Validation: conditional     [✅ Working]
    │       └── CTA URL Validation: HTTP/HTTPS       [✅ Working]
    │
    ├── 3. AI Enrichment
    │   └── AIService.enrich_content()               [🟡 70% COMPLETE]
    │       ├── OpenAI Provider: GPT-4o-mini         [✅ Working]
    │       ├── Ollama Provider: Local models        [✅ Working]  
    │       ├── Vision Processing: Alt text gen      [❌ Not implemented]
    │       │   ├── OpenAI Vision API: gpt-4o        [❌ Missing]
    │       │   └── Qwen 2.5VL: Local model          [❌ Missing]
    │       └── Brand Voice: Basic scoring           [✅ Working]
    │
    ├── 4. Platform Integration
    │   └── MarketingPlatformFactory.add_to_list()  [🟡 30% COMPLETE]
    │       ├── Mock Service: Full implementation    [✅ Working]
    │       ├── Marketo REST API: Real integration   [❌ Stub only]
    │       └── HubSpot API: Real integration        [❌ Stub only]
    │
    └── 5. Audit Logging
        └── append_activation_log()                  [🟢 95% COMPLETE]
            ├── JSONL Format: Structured logging    [✅ Working]
            ├── Non-blocking: Error tolerance       [✅ Working]
            └── File Rotation: Large file handling  [❌ Minor gap]
```

## Critical Path Analysis

### Demo Blockers (Must Fix)
1. **ContentfulService Mock → Live** 
   - **Current**: Returns hardcoded article data
   - **Needed**: Real Contentful SDK integration
   - **Impact**: Cannot demo with actual client content
   - **Estimate**: 12-16 hours

### High Value Features (Should Fix)
2. **Vision Alt Text Generation**
   - **Current**: Manual alt text validation only
   - **Needed**: Automatic generation via AI vision models
   - **Impact**: 26% accessibility compliance gap unaddressed
   - **Estimate**: 16-20 hours

### Production Readiness (Nice to Have)  
3. **Real Marketing Platform APIs**
   - **Current**: Mock service simulates platform responses
   - **Needed**: Actual Marketo/HubSpot API integration
   - **Impact**: Cannot complete full content-to-campaign workflow
   - **Estimate**: 8-12 hours

## Dependency Risk Assessment

### External Service Dependencies
```
Current System
├── Contentful CMS
│   ├── Status: Mock implementation only          [🔴 HIGH RISK]
│   ├── Required: Space ID, Access Tokens        [❌ Not configured]
│   └── Content Model: Article schema            [❌ Not created]
│
├── OpenAI API  
│   ├── Status: GPT-4o-mini working              [🟢 LOW RISK]
│   ├── Vision API: Not integrated               [🟡 MEDIUM RISK]
│   └── Rate Limiting: Handled gracefully        [✅ Working]
│
├── Ollama (Local AI)
│   ├── Status: Text models working              [🟢 LOW RISK]  
│   ├── Vision Models: Qwen 2.5VL not setup     [🟡 MEDIUM RISK]
│   └── Fallback: Graceful degradation          [✅ Working]
│
└── Marketing Platforms
    ├── Marketo: Mock only                       [🟡 MEDIUM RISK]
    ├── HubSpot: Mock only                       [🟡 MEDIUM RISK]  
    └── Mock Service: Full functionality         [🟢 LOW RISK]
```

### Internal Component Dependencies
```
FastAPI Application (main.py)
├── Dependencies: All internal services loaded    [🟢 LOW RISK]
├── Error Handling: Comprehensive coverage       [🟢 LOW RISK]
├── Rate Limiting: Per-client IP tracking        [🟢 LOW RISK]
└── Health Checks: System status monitoring      [🟢 LOW RISK]

Pydantic Schemas (schemas/*.py)
├── ArticleIn: Validation logic complete         [🟢 LOW RISK]
├── ActivationPayload: Request handling          [🟢 LOW RISK]
└── ActivationResult: Response formatting        [🟢 LOW RISK]

Test Suite Coverage
├── Backend: 23 tests, all passing              [🟢 LOW RISK]
├── Frontend: 7 tests, all passing              [🟢 LOW RISK]
└── Integration: Mock services tested            [🟡 MEDIUM RISK - needs real API tests]
```

## Service Integration Points

### Contentful → Backend Integration
```
Current Flow (Mock):
ContentfulService.get_article(entry_id)
    └── Returns: Hardcoded sample article data

Required Flow (Live):
ContentfulService.get_article(entry_id)
    ├── contentful.Client.entry(entry_id)
    ├── Transform rich text → plain text
    ├── Resolve asset URLs → image references  
    ├── Map Contentful fields → ArticleIn schema
    └── Handle missing fields gracefully
```

### AI Service → Vision Integration  
```
Current Flow (Text Only):
AIService.enrich_content(article_data)
    ├── Generate meta description
    ├── Extract keywords  
    └── Analyze brand voice

Enhanced Flow (With Vision):
AIService.enrich_content(article_data)
    ├── Text processing (existing)
    ├── Image analysis (if has_images=true)
    │   ├── gpt-4o vision API call
    │   ├── Generate contextual alt text
    │   └── Quality validation
    └── Combined results
```

### Backend → Marketing Platform Integration
```
Current Flow (Mock):
MarketingPlatformFactory.add_to_list(payload)
    └── MockService: Simulated 250ms response

Production Flow (Live):
MarketingPlatformFactory.add_to_list(payload)  
    ├── Marketo: REST API authentication
    ├── HubSpot: Contact/list management
    ├── Error handling & retries
    └── Response validation
```

## Scalability Considerations

### Agent Specialization Points
When the system grows beyond single-developer scope:

1. **Content Management Agent**: Handles Contentful integration complexities
2. **Vision Processing Agent**: Specializes in image analysis and alt text generation  
3. **Marketing Platform Agent**: Manages multiple platform API integrations
4. **Testing Agent**: Handles end-to-end validation across real services

### Dependency Complexity Thresholds
- **Current**: 6 core components, manageable manually
- **Phase 2**: 10-15 components, simple tooling helpful
- **Phase 3**: 20+ components, automated dependency analysis valuable
- **Enterprise**: 50+ components, full adaptive workflow recommended

## Next Actions by Priority

### CRITICAL (Required for Demo)
1. **Setup Contentful Space**: Create account, content model, sample articles
2. **Install Contentful SDK**: Add to requirements.txt, implement real client
3. **Replace Mock Service**: ContentfulService → Live integration
4. **End-to-End Testing**: Verify real content retrieval and processing

### HIGH VALUE (Major Feature Gap)  
5. **Vision Model Setup**: Install and configure Qwen 2.5VL locally
6. **OpenAI Vision Integration**: Add gpt-4o image analysis capabilities
7. **Alt Text Pipeline**: Build end-to-end automated generation workflow

### MEDIUM PRIORITY (Production Readiness)
8. **Marketo API Integration**: Replace stub with real REST API calls
9. **HubSpot API Integration**: Implement contact and list management  
10. **Enhanced Error Handling**: Production-grade resilience patterns

---

*This dependency map reflects the current system state as of the most recent code analysis. All status assessments are based on verified implementation review, not assumptions.*