# Vision Alt Text Generation Feature Spec

> Spec: vision-alt-text-generation
> Created: 2025-01-06
> Status: Planning

## Overview

Add automated alt text generation for images using vision-capable AI models (GPT-4o Vision and Qwen 2.5VL 7b). This feature addresses the industry problem where only 26% of sites have proper alt text, ensuring accessibility compliance and SEO optimization for all activated content.

## Technical Requirements

### Vision Model Integration
- **Primary Model**: GPT-4o Vision API for high-quality commercial alt text
- **Local Alternative**: Qwen 2.5VL 7b model via Ollama for cost-effective processing
- **Provider Switching**: Environment-based model selection (similar to existing AI service)
- **Input Support**: JPEG, PNG, WebP images up to 10MB
- **Context Awareness**: Generate alt text that considers article topic and campaign tags

### Image Processing Pipeline
- **Image Retrieval**: Fetch images from Contentful assets or external URLs
- **Format Validation**: Ensure supported image formats and sizes
- **Preprocessing**: Resize/compress if needed for model compatibility
- **Vision Analysis**: Generate descriptive alt text using selected model
- **Quality Validation**: Ensure alt text meets accessibility standards (meaningful, concise)

### Integration with Existing Workflow
- **ArticleIn Validation**: Automatically generate alt text when `has_images=true` and `alt_text` is missing
- **Override Support**: Allow manual alt text to take precedence over generated text
- **Batch Processing**: Handle multiple images within single article
- **Error Handling**: Graceful degradation when vision models unavailable

### Accessibility Standards Compliance
- **Length**: Alt text between 10-150 characters (optimal for screen readers)
- **Content Quality**: Descriptive, specific, avoiding redundant phrases like "image of"
- **Context Relevance**: Alt text should relate to article content and purpose
- **WCAG 2.1 Compliance**: Meet Level AA accessibility guidelines

## Acceptance Criteria

1. **Automatic Generation**: Generate alt text when article has images but missing alt_text
2. **Model Selection**: Support both GPT-4o Vision and local Qwen 2.5VL models
3. **Quality Standards**: Generated alt text meets accessibility best practices
4. **Context Awareness**: Alt text reflects article topic and marketing intent
5. **Error Resilience**: Continue activation even when vision models fail
6. **Performance**: Vision processing adds <3 seconds to activation time
7. **Cost Control**: Configurable model selection based on budget preferences

## Integration Points

### Existing Code Extensions Required

**File**: `backend/services/ai_service.py`
- Add vision model capabilities alongside existing text models
- Implement `generate_alt_text(image_url, context)` method
- Add model switching logic for vision providers
- Handle image preprocessing and API calls

**File**: `backend/schemas/article.py`
- Update ArticleIn validation to trigger alt text generation
- Add `image_urls` field for explicit image URL specification
- Modify alt text validation to allow generated content

**File**: `backend/main.py`
- Integrate alt text generation into activation workflow
- Add vision processing to enrichment pipeline
- Handle vision model failures gracefully

### New Service Components

**VisionService Class** (new: `backend/services/vision_service.py`)
```python
class VisionService:
    def __init__(self, provider: str = "openai"):
        self.provider = provider

    async def generate_alt_text(
        self,
        image_url: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate alt text for image with article context."""
        pass

    def validate_alt_text(self, alt_text: str) -> bool:
        """Validate alt text meets accessibility standards."""
        pass
```

### Model Configuration

**GPT-4o Vision Setup**
```python
# OpenAI vision model integration
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_alt_text_openai(image_url: str, context: dict) -> str:
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": ALT_TEXT_PROMPT.format(**context)},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]
    )
    return response.choices[0].message.content
```

**Qwen 2.5VL Local Setup**
```python
# Ollama local model integration
import ollama

def generate_alt_text_local(image_url: str, context: dict) -> str:
    response = ollama.chat(
        model='qwen2.5vl:7b',
        messages=[
            {
                'role': 'user',
                'content': ALT_TEXT_PROMPT.format(**context),
                'images': [image_url]
            }
        ]
    )
    return response['message']['content']
```

## Vision Model Prompting Strategy

### Context-Aware Alt Text Prompt
```python
ALT_TEXT_PROMPT = """
Generate accessible alt text for this image within the context of a marketing article.

Article Context:
- Title: {title}
- Campaign Tags: {campaign_tags}
- Content Type: {content_type}
- Target Audience: {audience}

Alt Text Requirements:
1. 10-150 characters in length
2. Describe what's visible, not what it means
3. Be specific and descriptive
4. Avoid starting with "Image of" or "Picture of"
5. Consider marketing context but focus on visual content
6. Include relevant technical details if present (UI elements, charts, etc.)

Generate only the alt text, no explanations or quotes.
"""
```

### Quality Validation Criteria
```python
def validate_alt_text_quality(alt_text: str) -> Dict[str, Any]:
    """Validate generated alt text meets standards."""
    return {
        "length_valid": 10 <= len(alt_text) <= 150,
        "not_generic": not alt_text.lower().startswith(("image of", "picture of")),
        "descriptive": len(alt_text.split()) >= 3,
        "no_redundancy": "alt text" not in alt_text.lower(),
        "contextually_relevant": True  # Would need more sophisticated checking
    }
```

## Dependencies

### External Services
- **OpenAI API**: GPT-4o Vision access with sufficient credits
- **Ollama**: Local installation with Qwen 2.5VL 7b model downloaded
- **Image Access**: Ability to fetch images from Contentful assets or external URLs

### Technical Requirements
- **GPU Support**: Optional but recommended for local Qwen model performance
- **Memory**: Minimum 8GB RAM for local vision model processing
- **Network**: Reliable access to OpenAI API and image URLs
- **Storage**: ~4GB for Qwen 2.5VL 7b model download

### Configuration Requirements
```bash
# Vision model selection
VISION_PROVIDER=openai  # or 'local'
OPENAI_API_KEY=your_openai_key_here

# Local model configuration (if using Ollama)
OLLAMA_BASE_URL=http://localhost:11434
VISION_MODEL_NAME=qwen2.5vl:7b

# Processing limits
MAX_IMAGE_SIZE_MB=10
VISION_PROCESSING_TIMEOUT=30
```

## Risk Assessment

### High Risk
- **Model Availability**: OpenAI API outages or rate limiting could block activations
- **Cost Management**: Vision API calls can be expensive with high image volumes
- **Image Access**: Images hosted on restricted domains may not be accessible
- **Quality Variability**: Generated alt text may not always meet human quality standards

### Medium Risk
- **Performance Impact**: Vision processing adds latency to activation workflow
- **Local Model Setup**: Ollama and model installation complexity for local option
- **Memory Usage**: Local models require significant RAM/VRAM
- **Context Accuracy**: Vision models may misinterpret marketing-specific context

### Mitigation Strategies
- **Fallback Chain**: OpenAI → Ollama → Manual requirement (block activation)
- **Cost Controls**: Daily/monthly API usage limits and monitoring
- **Image Caching**: Cache generated alt text to avoid repeated processing
- **Quality Thresholds**: Validate generated content meets minimum standards
- **Manual Override**: Always allow human-provided alt text to take precedence

## Expected Deliverable

A vision-powered alt text generation system that:
1. Automatically generates alt text for articles with images
2. Supports both cloud (GPT-4o) and local (Qwen 2.5VL) vision models
3. Produces accessibility-compliant alt text (WCAG 2.1 Level AA)
4. Integrates seamlessly into existing activation workflow
5. Provides cost-effective local processing option
6. Maintains activation performance targets (<5 seconds total)

## Out of Scope (Future Iterations)

- Real-time image alt text generation during content creation
- Batch processing of existing content lacking alt text
- Advanced image analysis (OCR, chart reading, brand recognition)
- Multi-language alt text generation
- Custom vision model fine-tuning for specific content types
- Integration with Contentful asset management workflows

## Performance Targets

### Vision Processing Metrics
- **OpenAI Vision API**: <2 seconds per image (p95)
- **Local Qwen Model**: <5 seconds per image (p95, CPU) or <2 seconds (GPU)
- **Image Download**: <1 second for images under 5MB
- **Total Added Latency**: <3 seconds for single image article

### Quality Metrics
- **Accessibility Compliance**: 95%+ of generated alt text meets WCAG 2.1 standards
- **Context Relevance**: 90%+ of alt text appropriate for article topic
- **Character Length**: 95%+ within 10-150 character range
- **Human Approval Rate**: 85%+ of generated alt text acceptable without editing

### Cost Management
- **OpenAI Budget**: Configurable daily/monthly spending limits
- **Local Processing**: Zero marginal cost after initial setup
- **Cache Hit Rate**: 20%+ for repeated image processing
- **Error Rate**: <5% vision model failures requiring fallback
