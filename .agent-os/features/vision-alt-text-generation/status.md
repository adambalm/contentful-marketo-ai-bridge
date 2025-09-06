# Vision Alt Text Generation Status

> Last Updated: 2025-01-06
> Feature: vision-alt-text-generation  
> Status: Planning

## Current Implementation Status

### ✅ Completed (Foundation)
- Provider-agnostic AI service architecture (supports OpenAI and Ollama)
- Text-based AI enrichment with meta description and keyword generation
- ArticleIn schema with alt_text field validation  
- Alt text requirement validation when has_images=true
- Error handling patterns for AI service failures

### 🔨 In Progress
- None (feature not yet started)

### ⏳ Pending Implementation
- Vision-capable AI service integration (GPT-4o Vision, Qwen 2.5VL)
- Image processing pipeline (download, validate, preprocess)
- Context-aware alt text generation with article metadata
- Quality validation for accessibility compliance (WCAG 2.1)
- Integration with existing activation workflow
- Cost control and caching mechanisms

## Technical Debt

### Current Limitations
- **Manual Alt Text Only**: No automated generation for images
- **Limited Accessibility Validation**: Basic presence check, no quality validation
- **No Image Processing**: No support for image analysis or vision models
- **Static Requirements**: Alt text must be provided manually or activation fails
- **Missing Context**: Alt text generated without article context awareness

### Performance Gaps
- **Industry Standards**: Only 26% of sites have proper alt text - we can improve this
- **Accessibility Compliance**: No validation against WCAG 2.1 standards
- **User Experience**: Content creators must manually write alt text for every image
- **Workflow Efficiency**: No automation to speed up content activation process

## Implementation Risks

### High Priority
- **Model Availability**: OpenAI GPT-4o Vision API outages could block activations
- **Cost Control**: Vision API calls significantly more expensive than text-only
- **Quality Consistency**: Generated alt text may not meet human quality standards
- **Processing Latency**: Vision processing could slow activation beyond 5-second target

### Medium Priority
- **Local Model Setup**: Ollama and Qwen 2.5VL installation complexity
- **Memory Requirements**: Local vision models need significant RAM/VRAM
- **Image Access**: Some images may be hosted on inaccessible domains
- **Context Accuracy**: Vision models may misinterpret marketing-specific context

### Low Priority
- **Cache Management**: Image caching storage and cleanup overhead  
- **Format Support**: Limited to common web formats (JPEG, PNG, WebP)
- **Batch Processing**: Multiple images in single article add complexity
- **Model Updates**: Vision model versions may change API compatibility

## Dependencies

### External Services
- **OpenAI API**: GPT-4o Vision access requires upgraded API plan
- **Ollama Installation**: Local model server for cost-effective alternative
- **Image Hosting**: Reliable access to images via HTTP/HTTPS URLs
- **Network Connectivity**: Stable internet for API calls and image downloads

### Technical Infrastructure  
- **GPU Support**: Optional but recommended for local Qwen model performance
- **Memory Resources**: Minimum 8GB RAM for local vision model processing
- **Storage Space**: ~4GB for Qwen 2.5VL 7b model download
- **Processing Power**: Sufficient CPU for image preprocessing and analysis

### Development Requirements
- **Test Images**: Collection of sample images for development and testing
- **Accessibility Expertise**: Understanding of WCAG 2.1 standards and best practices
- **Prompt Engineering**: Optimize prompts for context-aware alt text generation
- **Cost Monitoring**: Track API usage and implement budget controls

## Next Steps

### Immediate (Next Sprint)
1. **Environment Setup**
   - Install Ollama and download Qwen 2.5VL 7b model
   - Test OpenAI GPT-4o Vision API access
   - Create test image collection for development

2. **Service Architecture** 
   - Design VisionService class with provider abstraction
   - Plan integration with existing AI service
   - Define image processing pipeline

### Short Term (2-3 Sprints)
3. **Core Implementation**
   - Implement vision model integration (OpenAI + Ollama)
   - Create alt text generation with contextual prompting
   - Build quality validation for accessibility standards

4. **Workflow Integration**
   - Integrate vision processing into activation workflow
   - Add error handling and fallback mechanisms
   - Update schemas and validation logic

### Long Term (4+ Sprints)  
5. **Optimization and Monitoring**
   - Implement caching for cost and performance optimization
   - Add usage monitoring and cost controls
   - Create quality metrics and improvement feedback loops

## Performance Targets

### Current Performance (Manual Alt Text)
- Alt text validation: ~1ms (simple presence check)
- Activation with alt text: ~2-3 seconds total
- Accessibility compliance: Depends on manual quality

### Target Performance (Automated Vision)
- **OpenAI Vision**: <2 seconds per image (API call + processing)  
- **Local Qwen**: <5 seconds per image (CPU) or <2 seconds (GPU)
- **Total Added Latency**: <3 seconds for typical single-image article
- **Accessibility Compliance**: 95%+ WCAG 2.1 Level AA compliance

### Cost Considerations
- **OpenAI Vision**: ~$0.01-0.02 per image (varies by resolution)
- **Local Processing**: Zero marginal cost after setup
- **Caching Savings**: 20-30% reduction through duplicate detection
- **Budget Controls**: Configurable daily/monthly spending limits

## Configuration Planning

### Environment Variables (New)
```bash
# Vision model selection
VISION_PROVIDER=openai  # or 'local' or 'hybrid'
VISION_FALLBACK_PROVIDER=local

# OpenAI configuration  
OPENAI_API_KEY=sk-proj-your_key_here
OPENAI_VISION_MODEL=gpt-4o

# Local model configuration
OLLAMA_BASE_URL=http://localhost:11434
VISION_MODEL_NAME=qwen2.5vl:7b

# Processing controls
MAX_IMAGE_SIZE_MB=10
VISION_PROCESSING_TIMEOUT=30
VISION_CACHE_TTL_HOURS=24
VISION_DAILY_BUDGET_USD=50
```

### Dependencies (backend/requirements.txt)
```python
# Vision processing
ollama>=0.1.9
Pillow>=10.0.0

# Already have OpenAI client for text processing
# openai>=1.3.0  # (existing)
```

## Impact Assessment

### Positive Impact
- **Accessibility**: Automatic alt text ensures WCAG compliance for all activated content
- **Efficiency**: Content creators no longer need to manually write alt text
- **Quality**: Consistent, contextual alt text generated using article context
- **Industry Leadership**: Address the 26% alt text gap proactively

### Potential Challenges  
- **Cost**: Vision API calls more expensive than current text-only processing
- **Latency**: Additional processing time may impact user experience
- **Quality Control**: Generated content may require human review/editing  
- **Complexity**: Additional failure modes and configuration requirements

### Mitigation Strategies
- **Hybrid Approach**: OpenAI for quality, Ollama for cost control
- **Smart Caching**: Avoid reprocessing identical images
- **Quality Thresholds**: Automatic validation with human review triggers
- **Gradual Rollout**: Optional feature initially, mandatory as quality improves

## Success Criteria

### Technical Milestones
- [ ] Both OpenAI and Ollama vision models successfully integrated
- [ ] Vision processing adds <3 seconds to activation workflow
- [ ] 95%+ of generated alt text meets WCAG 2.1 Level AA standards
- [ ] Graceful fallback when vision models unavailable
- [ ] Cost controls prevent budget overruns

### Quality Milestones
- [ ] 90%+ context relevance based on article topic and tags
- [ ] 85%+ human acceptance rate without editing
- [ ] 95%+ character length compliance (10-150 characters)
- [ ] <5% generic phrase usage ("image of", "picture of")
- [ ] Consistent quality across image types (screenshots, photos, charts)

### User Experience Milestones
- [ ] Content creators can activate content without manual alt text
- [ ] Clear feedback when vision processing fails or produces low-quality results
- [ ] Option to override generated alt text with manual content
- [ ] Transparent cost reporting for OpenAI usage
- [ ] Setup documentation enables easy configuration