# User Stories

## Primary User Persona: Maria - Marketing Operations Manager

**Background**: Maria works at a B2B SaaS company and manages content activation workflows between Contentful CMS and marketing automation platforms. She's responsible for ensuring content meets brand standards and reaches campaign audiences efficiently.

**Pain Points**:
- Manual content tagging and validation takes 2-3 days per campaign
- Inconsistent brand voice across content pieces
- Missing metadata leads to poor SEO performance (35% missing meta descriptions)
- Missing alt text creates accessibility compliance issues (26% of sites lack proper alt text)
- No audit trail for AI-assisted content modifications
- Context switching between multiple tools and platforms

---

## Epic 1: Content Activation Workflow

### Story 1.1: Manual Content Activation
**As** Maria, a Marketing Operations Manager  
**I want** to manually trigger content activation from within the Contentful sidebar  
**So that** I can control when content gets processed and syndicated to marketing platforms  

**Acceptance Criteria**:
- ✅ "Activate in Marketo" button appears in Contentful entry sidebar
- ✅ Button triggers FastAPI backend processing
- ✅ Loading states and success/error notifications shown
- ✅ Activation process completes in <5 seconds

### Story 1.2: Content Validation & Accessibility
**As** Maria, a Marketing Operations Manager  
**I want** content to be automatically validated against our controlled vocabulary and accessibility standards  
**So that** I can ensure compliance with our content governance and accessibility requirements  

**Acceptance Criteria**:
- ✅ Pydantic schema validates 25+ marketing tags from controlled vocabulary
- ✅ Validation errors show specific feedback about invalid tags
- [ ] Automated alt text generation when images detected but alt text missing
- ✅ CTA format validation (max 80 chars, valid URLs)
- [ ] Vision model integration (Qwen 2.5VL 7b local, gpt-4o production)

### Story 1.3: AI Content Enrichment
**As** Maria, a Marketing Operations Manager  
**I want** AI to automatically generate meta descriptions and keywords  
**So that** I can ensure 100% SEO metadata coverage without manual effort  

**Acceptance Criteria**:
- ✅ OpenAI integration generates <160 char meta descriptions
- ✅ 3-7 relevant keywords extracted for campaign targeting
- ✅ Provider-agnostic AI service (OpenAI/Ollama switching)
- ✅ Graceful fallback if AI service unavailable

---

## Epic 2: Brand Compliance & Audit

### Story 2.1: Brand Voice Analysis
**As** Maria, a Marketing Operations Manager  
**I want** AI to analyze content against our brand voice guidelines  
**So that** I can maintain consistency across all marketing materials  

**Acceptance Criteria**:
- ✅ Categorical scoring for professionalism, accessibility, action-orientation
- ✅ "Pass/Advisory/Attention" ratings with specific improvement suggestions
- ✅ Non-blocking analysis (never prevents content activation)
- ✅ Results logged in ActivationLog for trend analysis

### Story 2.2: Complete Audit Trail
**As** Maria, a Marketing Operations Manager  
**I want** every activation to be logged with complete details  
**So that** I can demonstrate compliance and track AI decision-making  

**Acceptance Criteria**:
- ✅ JSONL format logging for every activation attempt
- ✅ Captures validation results, AI outputs, platform responses
- ✅ Unique activation ID for tracking and debugging
- ✅ Timestamp and processing time metrics included

---

## Epic 3: Platform Integration & Resilience

### Story 3.1: Marketing Platform Flexibility
**As** Maria, a Marketing Operations Manager  
**I want** to switch between different marketing platforms (Marketo, HubSpot)  
**So that** I can adapt to changing business requirements without code changes  

**Acceptance Criteria**:
- ✅ Marketing platform factory pattern implemented
- ✅ Environment-based platform switching
- ✅ Mock services for development/testing continuity
- ✅ Consistent interface across all platform implementations

### Story 3.2: Graceful Error Handling
**As** Maria, a Marketing Operations Manager  
**I want** the system to continue working even when external services fail  
**So that** I can maintain productivity during service outages  

**Acceptance Criteria**:
- ✅ Rate limiting prevents API quota exhaustion
- ✅ Mock services activate when real services unavailable
- ✅ Comprehensive error messages with actionable guidance
- ✅ Partial success scenarios handled appropriately

---

## Epic 4: Developer Experience & Quality

### Story 4.1: Professional Development Standards
**As** a developer joining the project  
**I want** comprehensive testing and quality gates  
**So that** I can contribute confidently without breaking existing functionality  

**Acceptance Criteria**:
- ✅ 30 test cases with 100% core business logic coverage
- ✅ Pre-commit hooks enforce code formatting and linting
- ✅ Black and Ruff integration for consistent code style
- ✅ All external dependencies mocked in tests

### Story 4.2: Portfolio Demonstration
**As** Maria's manager reviewing this portfolio project  
**I want** clear documentation and professional presentation  
**So that** I can assess technical capability and architectural thinking  

**Acceptance Criteria**:
- ✅ Comprehensive README with architecture diagrams
- ✅ Technical specification documenting design decisions
- ✅ Professional code organization and naming conventions
- ✅ Agent OS product documentation structure

---

## Secondary User: Content Creator

### Story 5.1: Content Guidelines Feedback
**As** a content creator using Contentful  
**I want** immediate feedback on brand voice compliance  
**So that** I can improve my content before submitting for activation  

**Future Enhancement**:
- Real-time brand voice analysis during content editing
- Inline suggestions for improvement
- Content template recommendations

### Story 5.2: Performance Insights
**As** a content creator  
**I want** to see how my activated content performs in campaigns  
**So that** I can learn what content types drive the best results  

**Future Enhancement**:
- Dashboard showing activation success rates
- Campaign performance correlation with content attributes
- A/B testing insights for content optimization

---

## User Journey: Complete Activation Workflow

1. **Content Creation**: Maria reviews new blog post in Contentful
2. **Validation Check**: Ensures required fields are populated and compliant
3. **Activation Trigger**: Clicks "Activate in Marketo" in sidebar
4. **AI Processing**: System validates, enriches with meta data, generates alt text for images, analyzes brand voice
5. **Platform Sync**: Content metadata pushed to marketing platform list
6. **Audit Logging**: Complete interaction logged for compliance
7. **Success Confirmation**: Maria sees activation confirmation with audit trail link

**Time Reduction**: 2-3 days → <5 seconds for content activation workflow