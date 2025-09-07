# Brand Voice Analysis Technical Specification

This is the technical specification for the automated brand voice compliance analysis system ensuring content consistency and quality in the AI Content Activation Engine.

> Created: 2025-09-06
> Version: 1.0.0
> Status: Implemented ✅
> Reference: @.agent-os/product/mission.md Brand Voice Heuristics

## Technical Requirements

### Core Functionality
- **Automated Brand Analysis**: Evaluate content against Contentful's brand voice guidelines
- **Categorical Scoring**: Provide pass/advisory results for specific brand dimensions
- **Content Quality Assurance**: Identify and flag brand voice compliance issues
- **Continuous Monitoring**: Track brand voice consistency across all content activations

### Brand Voice Dimensions
- **Professionalism**: Assess professional tone and language appropriateness
- **Dual-Audience Accessibility**: Evaluate content accessibility for both technical and business audiences
- **Action-Oriented Language**: Analyze use of clear, actionable language and CTAs
- **Brand Consistency**: Ensure alignment with established brand voice patterns

### Analysis Requirements
- **Content Coverage**: Analyze title, body, meta description, and generated content
- **Context Awareness**: Consider content type, audience, and campaign objectives
- **Real-Time Analysis**: Provide immediate feedback during content activation
- **Historical Tracking**: Maintain brand voice performance over time for improvement insights

### Performance Requirements
- **Analysis Speed**: <1 second for comprehensive brand voice analysis
- **Accuracy**: 90%+ accuracy in brand voice compliance detection
- **Consistency**: Reproducible results across similar content and contexts
- **Scalability**: Support concurrent analysis for multiple content activations

## Approach

### Architecture Pattern
```python
# Brand voice analysis interface
class BrandVoiceAnalyzer:
    def __init__(self):
        self.brand_guidelines = self._load_brand_guidelines()
        self.scoring_criteria = self._load_scoring_criteria()

    def analyze_content(self, content: Dict, context: Dict = None) -> BrandVoiceResult:
        """Comprehensive brand voice analysis"""
        return BrandVoiceResult(
            overall_score=self._calculate_overall_score(content),
            professionalism=self._analyze_professionalism(content),
            accessibility=self._analyze_accessibility(content),
            action_oriented=self._analyze_action_orientation(content),
            consistency=self._analyze_consistency(content, context),
            recommendations=self._generate_recommendations(content)
        )

    def _analyze_professionalism(self, content: Dict) -> CategoryResult:
        """Analyze professional tone and language"""
        pass

    def _analyze_accessibility(self, content: Dict) -> CategoryResult:
        """Analyze dual-audience accessibility"""
        pass

    def _analyze_action_orientation(self, content: Dict) -> CategoryResult:
        """Analyze action-oriented language and CTAs"""
        pass
```

### Implementation Strategy
1. **Brand Guideline Definition**: Codify Contentful's brand voice principles into analyzable criteria
2. **Content Analysis Engine**: Implement rule-based and heuristic analysis for each brand dimension
3. **Scoring System**: Categorical scoring with clear pass/advisory/fail thresholds
4. **Contextual Analysis**: Consider content type, audience, and campaign context in analysis
5. **Recommendation Engine**: Provide specific, actionable feedback for brand voice improvements

### Integration Points
- **Content Activation Pipeline**: Integrate analysis into existing content enrichment workflow
- **AI Service Integration**: Analyze both original and AI-enhanced content for consistency
- **ActivationLog Integration**: Record brand voice analysis results for audit and improvement
- **Quality Gates**: Block content activation for critical brand voice violations

## Brand Voice Criteria

### Professionalism Analysis
```python
class ProfessionalismAnalyzer:
    def __init__(self):
        self.professional_indicators = [
            "clear technical explanations",
            "industry-standard terminology",
            "formal but approachable tone",
            "expertise demonstration"
        ]
        self.unprofessional_patterns = [
            "excessive casual language",
            "unclear jargon",
            "overly complex explanations",
            "inappropriate informality"
        ]

    def analyze(self, content: str) -> CategoryResult:
        professional_score = self._score_professional_indicators(content)
        unprofessional_penalty = self._score_unprofessional_patterns(content)

        final_score = max(0, professional_score - unprofessional_penalty)

        return CategoryResult(
            category="professionalism",
            score=final_score,
            status="pass" if final_score >= 0.7 else "advisory",
            details=self._generate_professional_feedback(content)
        )
```

### Dual-Audience Accessibility Analysis
```python
class AccessibilityAnalyzer:
    def analyze(self, content: str) -> CategoryResult:
        """Analyze content accessibility for both technical and business audiences"""
        technical_clarity = self._analyze_technical_clarity(content)
        business_relevance = self._analyze_business_relevance(content)
        explanation_quality = self._analyze_explanation_quality(content)

        accessibility_score = (technical_clarity + business_relevance + explanation_quality) / 3

        return CategoryResult(
            category="accessibility",
            score=accessibility_score,
            status="pass" if accessibility_score >= 0.75 else "advisory",
            details={
                "technical_clarity": technical_clarity,
                "business_relevance": business_relevance,
                "explanation_quality": explanation_quality,
                "recommendations": self._generate_accessibility_recommendations(content)
            }
        )
```

### Action-Oriented Language Analysis
```python
class ActionOrientedAnalyzer:
    def __init__(self):
        self.action_indicators = [
            "clear call-to-action phrases",
            "imperative verbs",
            "outcome-focused language",
            "next steps guidance"
        ]

    def analyze(self, content: str) -> CategoryResult:
        """Analyze action-oriented language and clear CTAs"""
        cta_presence = self._detect_call_to_action(content)
        action_verb_usage = self._analyze_action_verbs(content)
        outcome_focus = self._analyze_outcome_language(content)

        action_score = self._calculate_action_score(cta_presence, action_verb_usage, outcome_focus)

        return CategoryResult(
            category="action_oriented",
            score=action_score,
            status="pass" if action_score >= 0.6 else "advisory",
            details=self._generate_action_feedback(content)
        )
```

## Data Models

### BrandVoiceResult Model
```python
class CategoryResult(BaseModel):
    category: str
    score: float = Field(ge=0.0, le=1.0)
    status: str = Field(regex="^(pass|advisory|fail)$")
    details: Dict[str, Any]
    recommendations: List[str] = []

class BrandVoiceResult(BaseModel):
    overall_score: float = Field(ge=0.0, le=1.0)
    overall_status: str = Field(regex="^(pass|advisory|fail)$")

    professionalism: CategoryResult
    accessibility: CategoryResult
    action_oriented: CategoryResult
    consistency: CategoryResult

    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    content_id: Optional[str] = None
    recommendations: List[str] = []

    def get_failing_categories(self) -> List[str]:
        """Return categories that failed brand voice analysis"""
        return [
            result.category for result in [
                self.professionalism, self.accessibility,
                self.action_oriented, self.consistency
            ] if result.status == "fail"
        ]

    def get_advisory_categories(self) -> List[str]:
        """Return categories with advisory recommendations"""
        return [
            result.category for result in [
                self.professionalism, self.accessibility,
                self.action_oriented, self.consistency
            ] if result.status == "advisory"
        ]
```

### Brand Guidelines Configuration
```python
class BrandGuidelines(BaseModel):
    """Contentful brand voice guidelines configuration"""

    professionalism_criteria: Dict[str, Any] = {
        "tone": "professional but approachable",
        "technical_depth": "appropriate for audience level",
        "industry_expertise": "demonstrate platform knowledge",
        "clarity": "clear and concise explanations"
    }

    accessibility_criteria: Dict[str, Any] = {
        "dual_audience": "serve both technical and business users",
        "explanation_levels": "provide context for technical concepts",
        "business_relevance": "connect technical features to business value",
        "inclusive_language": "avoid excluding terminology"
    }

    action_orientation_criteria: Dict[str, Any] = {
        "call_to_action": "clear next steps for readers",
        "outcome_focus": "emphasize results and benefits",
        "actionable_advice": "provide specific implementation guidance",
        "engagement": "encourage reader interaction"
    }
```

## Analysis Implementation

### Content Analysis Pipeline
```python
class BrandVoiceAnalysisEngine:
    def __init__(self):
        self.professionalism_analyzer = ProfessionalismAnalyzer()
        self.accessibility_analyzer = AccessibilityAnalyzer()
        self.action_analyzer = ActionOrientedAnalyzer()
        self.consistency_analyzer = ConsistencyAnalyzer()

    def analyze_content(self, content: Dict, context: Dict = None) -> BrandVoiceResult:
        """Main analysis orchestration"""

        # Extract content text for analysis
        content_text = self._extract_content_text(content)

        # Run parallel analysis
        professionalism_result = self.professionalism_analyzer.analyze(content_text)
        accessibility_result = self.accessibility_analyzer.analyze(content_text)
        action_result = self.action_analyzer.analyze(content_text)
        consistency_result = self.consistency_analyzer.analyze(content_text, context)

        # Calculate overall score and status
        overall_score = self._calculate_overall_score([
            professionalism_result.score,
            accessibility_result.score,
            action_result.score,
            consistency_result.score
        ])

        overall_status = self._determine_overall_status(overall_score, [
            professionalism_result.status,
            accessibility_result.status,
            action_result.status,
            consistency_result.status
        ])

        return BrandVoiceResult(
            overall_score=overall_score,
            overall_status=overall_status,
            professionalism=professionalism_result,
            accessibility=accessibility_result,
            action_oriented=action_result,
            consistency=consistency_result,
            recommendations=self._generate_overall_recommendations(
                professionalism_result, accessibility_result,
                action_result, consistency_result
            )
        )
```

### Scoring System
```python
class BrandVoiceScoring:
    """Brand voice scoring methodology"""

    SCORE_THRESHOLDS = {
        "pass": 0.75,      # 75%+ score = pass
        "advisory": 0.60,   # 60-74% score = advisory
        "fail": 0.0         # <60% score = fail
    }

    CATEGORY_WEIGHTS = {
        "professionalism": 0.30,
        "accessibility": 0.30,
        "action_oriented": 0.25,
        "consistency": 0.15
    }

    @staticmethod
    def calculate_overall_score(category_scores: Dict[str, float]) -> float:
        """Calculate weighted overall brand voice score"""
        weighted_sum = sum(
            score * BrandVoiceScoring.CATEGORY_WEIGHTS.get(category, 0.25)
            for category, score in category_scores.items()
        )
        return min(1.0, max(0.0, weighted_sum))

    @staticmethod
    def determine_status(score: float) -> str:
        """Determine pass/advisory/fail status from score"""
        if score >= BrandVoiceScoring.SCORE_THRESHOLDS["pass"]:
            return "pass"
        elif score >= BrandVoiceScoring.SCORE_THRESHOLDS["advisory"]:
            return "advisory"
        return "fail"
```

## Integration with Content Pipeline

### Content Activation Integration
```python
# Integration in main activation flow
def activate_content(content_data: Dict) -> ActivationResult:
    try:
        # Existing validation
        article = ArticleIn(**content_data)

        # AI enrichment
        enriched_content = ai_service.enrich_content(article.dict())

        # Brand voice analysis
        brand_analysis = brand_voice_analyzer.analyze_content(
            content=enriched_content,
            context={"content_type": "article", "campaign_tags": article.campaign_tags}
        )

        # Quality gate - block activation for critical failures
        if brand_analysis.overall_status == "fail":
            critical_issues = brand_analysis.get_failing_categories()
            return ActivationResult(
                success=False,
                error=f"Brand voice compliance failed: {', '.join(critical_issues)}",
                brand_voice_analysis=brand_analysis
            )

        # Continue with platform publishing
        platform_result = marketing_platform.create_campaign(enriched_content)

        return ActivationResult(
            success=True,
            campaign_id=platform_result.campaign_id,
            brand_voice_analysis=brand_analysis,
            ai_enrichment=enriched_content,
            platform_response=platform_result
        )

    except Exception as e:
        return ActivationResult(success=False, error=str(e))
```

## Acceptance Criteria

### Functional Acceptance
- [ ] Analyze content across all four brand voice dimensions with accurate scoring
- [ ] Provide categorical pass/advisory/fail results with specific recommendations
- [ ] Generate actionable feedback for brand voice improvement
- [ ] Integrate seamlessly with existing content activation pipeline
- [ ] Block activation for critical brand voice compliance failures

### Performance Acceptance
- [ ] Complete brand voice analysis within 1-second response time requirement
- [ ] Achieve 90%+ accuracy in brand voice compliance detection
- [ ] Provide consistent, reproducible results across similar content
- [ ] Support concurrent analysis for multiple content activations
- [ ] Scale to handle high-volume content processing without performance degradation

### Quality Acceptance
- [ ] Brand voice criteria accurately reflect Contentful's brand guidelines
- [ ] Scoring system provides meaningful differentiation between content quality levels
- [ ] Recommendations are specific, actionable, and relevant to detected issues
- [ ] Analysis considers content context (type, audience, campaign objectives)
- [ ] Historical tracking enables brand voice improvement over time

### Integration Acceptance
- [ ] Brand voice results captured in ActivationLog for audit and analytics
- [ ] Analysis works with both original and AI-enhanced content
- [ ] Quality gates prevent publication of non-compliant content
- [ ] Results inform content optimization and improvement workflows
- [ ] API provides brand voice analysis as standalone service for other applications

## Quality Gates and Thresholds

### Scoring Thresholds
```python
BRAND_VOICE_THRESHOLDS = {
    "professionalism": {
        "pass": 0.75,
        "advisory": 0.60,
        "fail": 0.0
    },
    "accessibility": {
        "pass": 0.75,
        "advisory": 0.60,
        "fail": 0.0
    },
    "action_oriented": {
        "pass": 0.60,  # Lower threshold for action-oriented
        "advisory": 0.45,
        "fail": 0.0
    },
    "overall": {
        "pass": 0.75,
        "advisory": 0.60,
        "block_activation": 0.40  # Block activation below this threshold
    }
}
```

### Quality Gate Rules
1. **Pass Status**: All categories score above pass threshold
2. **Advisory Status**: Any category scores in advisory range, none fail
3. **Fail Status**: Any category scores below advisory threshold
4. **Activation Blocking**: Overall score below critical threshold (0.40)
5. **Manual Override**: Allow manual override for advisory status with justification

## Security and Privacy Considerations

### Content Privacy
- **Analysis Logging**: Log analysis results without exposing sensitive content
- **Temporary Storage**: Minimize temporary storage of content during analysis
- **Access Controls**: Restrict access to brand voice analysis results and recommendations

### Data Protection
- **Content Sanitization**: Remove personal or sensitive information before analysis
- **Result Anonymization**: Anonymize brand voice results for analytics and improvement
- **Retention Policy**: Define retention period for brand voice analysis data

## Extensibility Framework

### Custom Brand Guidelines
```python
# Framework for custom brand voice criteria
class CustomBrandGuidelines(BrandGuidelines):
    def __init__(self, organization_config: Dict):
        super().__init__()
        self.custom_criteria = organization_config.get("brand_criteria", {})
        self.scoring_weights = organization_config.get("scoring_weights", self.CATEGORY_WEIGHTS)

    def customize_analysis(self, analyzer_type: str, custom_rules: Dict):
        """Allow customization of analysis rules per organization"""
        pass
```

### Multi-Brand Support
```python
# Support for multiple brand voices
class MultiBrandAnalyzer:
    def __init__(self):
        self.brand_analyzers = {}

    def register_brand(self, brand_id: str, guidelines: BrandGuidelines):
        """Register brand-specific analysis configuration"""
        self.brand_analyzers[brand_id] = BrandVoiceAnalyzer(guidelines)

    def analyze_content(self, content: Dict, brand_id: str, context: Dict = None) -> BrandVoiceResult:
        """Analyze content against specific brand guidelines"""
        analyzer = self.brand_analyzers.get(brand_id, self.default_analyzer)
        return analyzer.analyze_content(content, context)
```
