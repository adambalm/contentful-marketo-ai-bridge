# Vision-Powered Alt Text Generation

## Implementation Status: NOT IMPLEMENTED ❌

**Current Reality:** No vision capabilities exist. Alt text field validation only.
**Industry Gap:** 26% of websites lack proper alt text for accessibility compliance.

## Problem Statement

Marketing content often contains images without proper alt text descriptions, creating accessibility barriers and missing SEO optimization opportunities. Manual alt text creation is time-intensive and inconsistent across content creators.

## Technical Specification

### Architecture Design

```
Image Upload → Vision Model → Alt Text Generation → Quality Validation → Storage
```

### Provider Requirements

#### Production Provider: OpenAI Vision ❌
- **Model**: gpt-4o (vision capabilities)
- **Input**: Image URL or base64-encoded image
- **Output**: Contextual alt text descriptions
- **Context**: Article title and body for relevant descriptions

#### Local Provider: Qwen 2.5VL 7b ❌
- **Model**: Qwen 2.5 Vision-Language 7b parameter model
- **Deployment**: Via Ollama local infrastructure
- **Performance**: Suitable for development and cost-conscious production
- **Privacy**: Complete local processing, no external API calls

### API Integration Points

#### New FastAPI Endpoints (NOT IMPLEMENTED)
```python
@app.post("/upload-image")
async def upload_image(file: UploadFile) -> ImageUploadResponse:
    """Accept image uploads for alt text generation"""

@app.post("/generate-alt-text")
async def generate_alt_text(payload: AltTextRequest) -> AltTextResponse:
    """Generate alt text from image and article context"""
```

#### Enhanced ArticleIn Schema (PARTIALLY EXISTS)
```python
class ArticleIn(BaseModel):
    # Current implementation has these fields:
    has_images: bool = Field(False)           # ✅ EXISTS
    alt_text: str | None = Field(None)        # ✅ EXISTS (validation only)

    # Needs addition:
    image_urls: List[str] = Field([])         # ❌ MISSING
    generated_alt_texts: List[str] = Field([]) # ❌ MISSING
```

### Vision Processing Pipeline

#### Image Processing Flow (NOT IMPLEMENTED)
1. **Upload Validation**
   - File format check (JPEG, PNG, WebP)
   - Size limits (max 10MB per image)
   - Malware scanning

2. **Context Assembly**
   - Article title and summary
   - Surrounding text context
   - Brand voice guidelines

3. **Vision Model Inference**
   - Image analysis via gpt-4o or Qwen 2.5VL
   - Context-aware description generation
   - Brand tone consistency

4. **Quality Validation**
   - Length limits (125-150 characters optimal)
   - Accessibility compliance check
   - SEO keyword integration

## Acceptance Criteria

### Image Upload Handling ❌
- [ ] Support JPEG, PNG, WebP formats
- [ ] File size validation (10MB max)
- [ ] Secure temporary storage
- [ ] Error handling for corrupted files

### OpenAI Vision Integration ❌
- [ ] gpt-4o vision API calls
- [ ] Base64 encoding for image transmission
- [ ] Context prompt engineering for relevant descriptions
- [ ] Rate limiting and quota management

### Qwen 2.5VL Local Integration ❌
- [ ] Ollama model installation and configuration
- [ ] Local image processing pipeline
- [ ] Performance optimization for 7b parameter model
- [ ] Comparison metrics vs OpenAI quality

### Quality Assurance ❌
- [ ] Alt text length optimization (125-150 chars)
- [ ] Accessibility guidelines compliance (WCAG 2.1)
- [ ] Brand voice consistency validation
- [ ] A/B testing framework for quality comparison

### Content Management Integration ❌
- [ ] Contentful asset field mapping
- [ ] Bulk processing for existing content
- [ ] Manual override capabilities
- [ ] Version history tracking

## Performance Requirements

### Response Time Targets
- **OpenAI Vision**: <10 seconds per image
- **Qwen 2.5VL Local**: <15 seconds per image
- **Batch Processing**: 50+ images per hour

### Quality Metrics
- **Accuracy**: >90% contextually relevant descriptions
- **Accessibility**: 100% WCAG 2.1 compliance
- **SEO Value**: Include relevant keywords from article context
- **Brand Consistency**: Pass brand voice analysis

## Integration with Existing Systems

### Current Alt Text Validation (EXISTS) ✅
```python
# backend/schemas/article.py:87-92
@field_validator("alt_text")
@classmethod
def validate_alt_text_when_images_present(cls, v, info):
    has_images = info.data.get("has_images", False)
    if has_images and not v:
        raise ValueError("Alt text is required when images present")
    return v
```

### Enhancement Required ❌
- Replace manual alt_text requirement with automatic generation
- Add generated_alt_texts array for multiple images
- Include confidence scores and quality metrics
- Enable manual review and override workflow

## Security Considerations

### Image Processing Security ❌
- [ ] File type validation beyond extension checking
- [ ] Malware scanning for uploaded images
- [ ] Secure temporary storage with auto-cleanup
- [ ] API key protection for vision services

### Privacy Compliance ❌
- [ ] GDPR-compliant image processing workflows
- [ ] Data retention policies for uploaded images
- [ ] User consent management for AI processing
- [ ] Audit trails for vision model usage

## Success Metrics

### Accessibility Impact
- **Target**: Eliminate 26% alt text gap for activated content
- **Measurement**: 100% alt text coverage for image-containing articles
- **Compliance**: WCAG 2.1 AA standard adherence

### Operational Efficiency
- **Time Savings**: Reduce manual alt text creation from 2-3 minutes to <10 seconds
- **Consistency**: 95% brand voice compliance across generated descriptions
- **Accuracy**: <5% manual override rate for generated alt text
