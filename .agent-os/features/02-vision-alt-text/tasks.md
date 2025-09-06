# Implementation Tasks: Vision Alt Text Generation

## Status: NOT IMPLEMENTED ❌
**Estimated Total Time:** 16-20 hours
**Priority:** HIGH (addresses 26% industry accessibility gap)

## Phase 1: Infrastructure Setup (4-6 hours)

### Task 1.1: Image Upload Endpoint
**Estimate**: 2 hours  
**Priority**: Critical

```python
# Add to backend/main.py
@app.post("/upload-image", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """Accept image uploads for alt text generation"""
```

**Acceptance Criteria:**
- [ ] Accept JPEG, PNG, WebP formats
- [ ] Validate file size (10MB max)
- [ ] Return secure temporary URL
- [ ] Error handling for invalid formats

**Implementation Steps:**
1. Add file upload dependencies to requirements.txt
2. Create image validation utilities
3. Implement secure temporary storage
4. Add comprehensive error handling
5. Write upload endpoint tests

### Task 1.2: Enhanced Data Schemas  
**Estimate**: 1 hour
**Priority**: Critical

```python
# Enhance backend/schemas/article.py
class ArticleIn(BaseModel):
    image_urls: List[str] = Field([], description="Image URLs for processing")
    generated_alt_texts: List[str] = Field([], description="AI-generated alt text")
    alt_text_confidence: List[float] = Field([], description="Confidence scores")
```

**Acceptance Criteria:**
- [ ] Support multiple images per article
- [ ] Include confidence scoring
- [ ] Maintain backward compatibility
- [ ] Pydantic validation for new fields

### Task 1.3: Vision Service Architecture
**Estimate**: 2 hours  
**Priority**: Critical

```python
# Create backend/services/vision_service.py
class VisionService(ABC):
    @abstractmethod
    def generate_alt_text(self, image_data: bytes, context: str) -> AltTextResult:
        pass
```

**Acceptance Criteria:**
- [ ] Abstract base class for providers
- [ ] Provider factory pattern
- [ ] Environment-based switching
- [ ] Error handling and fallbacks

## Phase 2: OpenAI Vision Integration (6-8 hours)

### Task 2.1: OpenAI Vision Provider
**Estimate**: 4 hours
**Priority**: High  

```python
class OpenAIVisionProvider(VisionService):
    def generate_alt_text(self, image_data: bytes, context: str) -> AltTextResult:
        """Generate alt text using gpt-4o vision API"""
```

**Implementation Details:**
- Use gpt-4o model with vision capabilities
- Base64 encode images for API transmission
- Include article context in prompt engineering
- Handle API rate limits and errors

**Acceptance Criteria:**
- [ ] gpt-4o vision API integration
- [ ] Context-aware prompt engineering
- [ ] Base64 image encoding
- [ ] Rate limiting compliance
- [ ] Graceful error handling

### Task 2.2: Context-Aware Prompt Engineering
**Estimate**: 2 hours
**Priority**: High

**Prompt Template:**
```
Analyze this image in the context of a marketing article titled "{title}".
Article summary: {summary}
Generate a concise, SEO-friendly alt text (125-150 characters) that:
1. Describes the visual content accurately
2. Relates to the article context
3. Includes relevant keywords: {keywords}
4. Maintains professional, accessible tone
```

**Acceptance Criteria:**
- [ ] Context-aware descriptions
- [ ] Optimal length (125-150 chars)
- [ ] Keyword integration
- [ ] Brand voice consistency

### Task 2.3: Quality Validation Pipeline
**Estimate**: 2 hours
**Priority**: Medium

**Validation Checks:**
- Length optimization (125-150 characters)
- WCAG 2.1 compliance verification  
- Brand voice scoring
- Keyword relevance assessment

**Acceptance Criteria:**
- [ ] Automated quality scoring
- [ ] WCAG compliance validation
- [ ] Brand voice analysis integration
- [ ] Confidence score calculation

## Phase 3: Local Vision Integration (4-6 hours)

### Task 3.1: Qwen 2.5VL Setup
**Estimate**: 2 hours
**Priority**: Medium

**Ollama Model Installation:**
```bash
ollama pull qwen2.5-vl:7b
ollama run qwen2.5-vl:7b
```

**Acceptance Criteria:**
- [ ] Qwen 2.5VL 7b model installation
- [ ] Ollama API integration
- [ ] Local inference pipeline
- [ ] Performance optimization

### Task 3.2: Local Vision Provider
**Estimate**: 3 hours
**Priority**: Medium

```python
class QwenVisionProvider(VisionService):
    def generate_alt_text(self, image_data: bytes, context: str) -> AltTextResult:
        """Generate alt text using Qwen 2.5VL local model"""
```

**Implementation Details:**
- HTTP requests to Ollama API (localhost:11434)
- Image preprocessing for local model
- Context prompt adaptation for Qwen
- Performance monitoring and optimization

**Acceptance Criteria:**
- [ ] Ollama API integration
- [ ] Image preprocessing pipeline  
- [ ] Context prompt optimization
- [ ] Performance benchmarking vs OpenAI

### Task 3.3: Provider Performance Comparison
**Estimate**: 1 hour
**Priority**: Low

**Metrics to Compare:**
- Response time (seconds)
- Alt text quality (human evaluation)
- Context relevance scoring
- Cost per generation

**Acceptance Criteria:**
- [ ] Automated benchmarking suite
- [ ] Quality comparison framework
- [ ] Performance metrics dashboard
- [ ] Cost analysis reporting

## Phase 4: Integration & Testing (2-4 hours)

### Task 4.1: Activation Workflow Integration
**Estimate**: 2 hours
**Priority**: High

**Enhancement to `/activate` endpoint:**
1. Check for images in article content
2. Generate alt text if missing
3. Update article data with generated descriptions
4. Log vision model usage in activation log

**Acceptance Criteria:**
- [ ] Seamless integration with existing workflow
- [ ] Automatic alt text generation
- [ ] ActivationLog enhancement
- [ ] Error handling preservation

### Task 4.2: Comprehensive Testing
**Estimate**: 2 hours  
**Priority**: Critical

**Test Cases:**
```python
def test_vision_alt_text_generation():
    """Test end-to-end alt text generation"""
    
def test_multiple_images_processing():
    """Test batch processing of multiple images"""
    
def test_vision_provider_fallback():
    """Test fallback when primary provider fails"""
    
def test_alt_text_quality_validation():
    """Test quality scoring and validation"""
```

**Coverage Requirements:**
- [ ] Vision provider selection
- [ ] Image format validation  
- [ ] Alt text quality scoring
- [ ] Error handling edge cases
- [ ] Performance under load

## Implementation Timeline

### Sprint 1 (Week 1): Infrastructure
- Image upload endpoint
- Enhanced schemas
- Vision service architecture
- Basic testing setup

### Sprint 2 (Week 2): OpenAI Integration  
- OpenAI vision provider
- Prompt engineering
- Quality validation
- Integration testing

### Sprint 3 (Week 3): Local Models
- Qwen 2.5VL setup
- Local vision provider
- Performance comparison
- End-to-end testing

## Risk Mitigation

### Technical Risks
- **OpenAI API Limits**: Implement caching and batch processing
- **Local Model Performance**: GPU acceleration consideration
- **Image Processing**: Robust error handling for corrupted files
- **Quality Consistency**: A/B testing framework for validation

### Resource Requirements
- **OpenAI Credits**: Estimated $50-100 for development and testing
- **Local GPU**: Optional but recommended for Qwen 2.5VL performance
- **Storage**: Temporary image storage with auto-cleanup
- **Bandwidth**: Image upload/download optimization

## Success Criteria

### Functional Requirements
- [ ] 100% alt text coverage for image-containing articles
- [ ] <10 second response time for OpenAI vision
- [ ] <15 second response time for local model
- [ ] 95% quality score for generated alt text

### Quality Metrics
- [ ] WCAG 2.1 AA compliance for all generated descriptions
- [ ] 90% contextual relevance to article content
- [ ] <5% manual override rate in production
- [ ] Brand voice consistency maintained