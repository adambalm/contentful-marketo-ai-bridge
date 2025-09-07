# Architectural Decisions

## ADR-001: Provider-Agnostic AI Architecture

**Date**: 2024-09-05
**Status**: Accepted
**Context**: Need for flexible AI provider integration without vendor lock-in

### Decision
Implement AI service factory pattern supporting multiple providers (OpenAI, Ollama) with environment-based switching.

### Rationale
- **Cost Flexibility**: Switch between paid (OpenAI) and free (local Ollama) models
- **Vendor Independence**: Avoid lock-in to single AI provider
- **Development Continuity**: Local models for development when API quotas exhausted
- **Future-Proofing**: Easy integration of new providers (Claude, Gemini, etc.)

### Implementation
```python
class AIService:
    def __init__(self):
        provider = os.getenv("AI_PROVIDER", "openai").lower()
        if provider == "local":
            self.provider = LocalModelProvider()
        else:
            self.provider = OpenAIProvider()
```

### Consequences
- ✅ Cost control and vendor flexibility achieved
- ✅ Development productivity improved with local models
- ⚠️ Provider-specific features must be abstracted
- ⚠️ Consistent interface required across all providers

---

## ADR-002: JSONL Audit Logging as Dual-Use Training Dataset

**Date**: 2024-09-04
**Status**: Accepted
**Context**: Need for audit compliance AND future AI fine-tuning capability

### Decision
Structure ActivationLog as JSONL format designed for both audit compliance and machine learning training data.

### Rationale
- **Enterprise Governance**: Complete audit trail for all AI decisions
- **Future ML Pipeline**: High-quality structured data for supervised fine-tuning
- **Regulatory Compliance**: Transparent AI decision-making process
- **Performance Analysis**: Track accuracy improvements over time

### Implementation
```python
class ActivationResult(BaseModel):
    activation_id: str
    timestamp: datetime
    validation_results: dict
    ai_enrichment: dict
    brand_voice_analysis: dict
    platform_response: dict
```

### Consequences
- ✅ Regulatory compliance achieved through comprehensive logging
- ✅ Future SFT pipeline enabled with quality training data
- ✅ Performance tracking and optimization metrics available
- ⚠️ Storage costs increase with comprehensive logging
- ⚠️ JSONL schema must remain stable for training compatibility

---

## ADR-003: Pydantic Data Contracts Over Runtime Validation

**Date**: 2024-09-03
**Status**: Accepted
**Context**: Need for robust data validation beyond Contentful's type system

### Decision
Use Pydantic v2 models as "data contracts" ensuring semantic validation of marketing-specific rules.

### Rationale
- **Enterprise Governance**: Enforce business rules at the data layer
- **Type Safety**: Catch validation errors before external API calls
- **Documentation**: Schemas serve as living documentation
- **IDE Support**: IntelliSense and type checking in development

### Implementation
```python
class ArticleIn(BaseModel):
    campaign_tags: List[str] = Field(..., min_items=1)

    @validator('campaign_tags')
    def validate_controlled_vocabulary(cls, v):
        allowed_tags = {...}  # 25+ marketing tags
        invalid_tags = set(v) - allowed_tags
        if invalid_tags:
            raise ValueError(f"Invalid tags: {invalid_tags}")
        return v
```

### Consequences
- ✅ Robust validation prevents downstream errors
- ✅ Business rules enforced consistently
- ✅ Clear error messages for content creators
- ⚠️ Schema changes require careful migration planning
- ⚠️ Validation logic must be maintained alongside business rules

---

## ADR-004: Marketing Platform Factory Pattern

**Date**: 2024-09-02
**Status**: Accepted
**Context**: Support for multiple marketing automation platforms with unified interface

### Decision
Implement factory pattern for marketing platforms (Marketo, HubSpot, Mock) with environment-based selection.

### Rationale
- **Client Flexibility**: Support different marketing platforms per deployment
- **Development Productivity**: Mock services for testing without API dependencies
- **Business Continuity**: Graceful fallback during service outages
- **Cost Management**: Mock services avoid unnecessary API calls during development

### Implementation
```python
class MarketingPlatformFactory:
    @staticmethod
    def create_service():
        platform = os.getenv("MARKETING_PLATFORM", "mock").lower()
        if platform == "marketo":
            return MarketoService()
        elif platform == "hubspot":
            return HubSpotService()
        return MockMarketingService()
```

### Consequences
- ✅ Platform flexibility achieved without code changes
- ✅ Development continuity with mock services
- ✅ Consistent interface across all platform implementations
- ⚠️ Mock services must accurately simulate real platform behaviors
- ⚠️ Feature parity challenges across different platforms

---

## ADR-005: Portfolio-Focused Mock Services Over Live Integration

**Date**: 2024-09-06 (Lanesborough Protocol Decision)
**Status**: Accepted
**Context**: Balancing demonstration capability with cost/risk management for portfolio project

### Decision
Prioritize comprehensive mock services and documentation over live API integration for portfolio demonstration.

### Rationale
- **Cost Control**: Avoid ongoing API expenses for demonstration project
- **Risk Management**: Prevent accidental API quota exhaustion or data issues
- **Professional Standards**: Mock services demonstrate enterprise testing practices
- **Portfolio Focus**: Technical capability more important than live data processing

### Lanesborough Protocol Resolution
- **Models**: GA (Gemini 2.5 Pro), IA (Claude 3.5 Sonnet)
- **Issue**: GA proposed live API integration; IA challenged scope appropriateness for portfolio project
- **Resolution Type**: Strategic scope correction through evidence-based challenge
- **Convergence**: "Portfolio Verification & Documentation Sprint" agreed via 3-turn handshake

### Implementation
- Comprehensive mock services simulating real API behaviors
- Professional documentation showcasing architectural decisions
- Test coverage validating business logic without external dependencies
- Clear separation between development/demo and production configurations

### Consequences
- ✅ Cost-effective portfolio demonstration achieved
- ✅ Professional testing practices demonstrated
- ✅ Zero ongoing API costs or risk exposure
- ✅ Technical capability clearly documented
- ⚠️ Mock accuracy must be validated against real API specifications
- ⚠️ Future production deployment requires real integration setup

---

## ADR-006: Comprehensive Testing Strategy

**Date**: 2024-09-01
**Status**: Accepted
**Context**: Professional software development requires robust testing coverage

### Decision
Implement comprehensive testing with external dependency mocking and 100% core business logic coverage.

### Rationale
- **Quality Assurance**: Catch regressions before deployment
- **Professional Standards**: Demonstrate enterprise development practices
- **Development Confidence**: Safe refactoring and feature additions
- **Portfolio Showcase**: Professional testing approach for job application

### Implementation
- 23 backend tests covering all business logic paths
- 7 frontend tests validating component behavior
- Pytest with mocking for all external API dependencies
- Pre-commit hooks enforcing test execution

### Consequences
- ✅ High confidence in code reliability
- ✅ Professional development practices demonstrated
- ✅ Safe refactoring and maintenance possible
- ⚠️ Test maintenance overhead with feature changes
- ⚠️ Mock accuracy must be validated against real services

---

## ADR-007: Pre-commit Quality Gates

**Date**: 2024-08-30
**Status**: Accepted
**Context**: Consistent code quality and formatting across all commits

### Decision
Implement automated pre-commit hooks for formatting (Black), linting (Ruff), and type checking.

### Rationale
- **Code Consistency**: Uniform formatting across all contributors
- **Quality Assurance**: Catch issues before they enter version control
- **Professional Standards**: Industry best practices for Python development
- **Developer Experience**: Automated tooling reduces manual quality checks

### Implementation
```yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
      - id: ruff-format
```

### Consequences
- ✅ Consistent code quality enforced automatically
- ✅ Reduced manual code review overhead
- ✅ Professional development workflow demonstrated
- ⚠️ Initial setup friction for new contributors
- ⚠️ Tool configuration must be maintained and updated

---

## Decision Impact Summary

| Decision | Business Impact | Technical Debt | Portfolio Value |
|----------|----------------|----------------|-----------------|
| Provider-Agnostic AI | High - Cost flexibility | Low | High |
| JSONL Dual-Use Logging | High - Future ML capability | Medium | High |
| Pydantic Data Contracts | High - Quality assurance | Low | High |
| Marketing Platform Factory | Medium - Client flexibility | Low | Medium |
| Portfolio-Focused Mocks | High - Cost control | Low | High |
| Comprehensive Testing | High - Quality confidence | Medium | High |
| Pre-commit Quality Gates | Medium - Consistency | Low | Medium |
| Vision Model Integration | High - Accessibility compliance | Medium | High |

---

## ADR-008: Vision Model Integration for Accessibility Compliance

**Date**: 2024-09-06
**Status**: Accepted
**Context**: Need for automated alt text generation to address accessibility compliance gaps

### Decision
Integrate vision models for automated alt text generation: OpenAI gpt-4o for production, Qwen 2.5VL 7b for local development.

### Rationale
- **Accessibility Compliance**: Address industry gap where 26% of sites lack proper alt text
- **Portfolio Enhancement**: Demonstrate advanced AI capabilities beyond text processing
- **Provider Consistency**: Maintain provider-agnostic pattern with vision capabilities
- **Cost Control**: Local vision model reduces API costs during development

### Implementation
```python
# Vision provider interface
class VisionProvider(ABC):
    @abstractmethod
    def generate_alt_text(self, image_url: str, context: str) -> str:
        pass

# OpenAI implementation
def generate_alt_text(self, image_url: str, context: str) -> str:
    response = self.client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": f"Generate accessible alt text for this image in context: {context}"},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        }]
    )
```

### Consequences
- ✅ Automated accessibility compliance reduces manual effort
- ✅ Enhanced AI capabilities demonstrate technical depth
- ✅ Maintains provider-agnostic architecture patterns
- ⚠️ Additional complexity in AI service integration
- ⚠️ Vision model accuracy varies between providers

---

**Overall Assessment**: Architectural decisions consistently prioritize professional development practices, cost control, and future extensibility while maintaining high code quality and comprehensive testing coverage. Vision integration enhances accessibility compliance and demonstrates advanced AI capabilities.
