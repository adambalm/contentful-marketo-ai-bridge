# Vision Alt Text Generation Tasks

These are the tasks to be completed for the spec detailed in @.agent-os/features/vision-alt-text-generation/spec.md

> Created: 2025-01-06
> Status: Ready for Implementation

## Tasks

### Phase 1: Environment Setup and Dependencies (3 hours)

**Task 1.1: Install Vision Model Dependencies**
- [ ] Add OpenAI vision support to existing AI service
- [ ] Install Ollama for local model support: `curl -fsSL https://ollama.com/install.sh | sh`
- [ ] Download Qwen 2.5VL model: `ollama pull qwen2.5vl:7b`
- [ ] Test Ollama API connectivity: `curl http://localhost:11434/api/tags`
- [ ] Add required packages to `backend/requirements.txt`:
  ```
  ollama>=0.1.9
  Pillow>=10.0.0
  requests>=2.31.0
  ```

**Task 1.2: Environment Configuration**
- [ ] Add vision-specific variables to `.env.template`:
  ```bash
  VISION_PROVIDER=openai  # or 'local'
  OPENAI_API_KEY=your_openai_key_here
  OLLAMA_BASE_URL=http://localhost:11434
  VISION_MODEL_NAME=qwen2.5vl:7b
  MAX_IMAGE_SIZE_MB=10
  VISION_PROCESSING_TIMEOUT=30
  ```
- [ ] Update `.env.example` with vision configuration
- [ ] Document model setup process in README

**Task 1.3: Test Vision Model Access**
- [ ] Create test script for OpenAI GPT-4o Vision API
- [ ] Create test script for Ollama Qwen 2.5VL local model
- [ ] Verify both models can process sample images
- [ ] Compare response quality and processing time
- [ ] Document model selection recommendations

### Phase 2: Vision Service Implementation (4 hours)

**Task 2.1: Create VisionService Class**
- [ ] **File**: `backend/services/vision_service.py` (new)
- [ ] Implement base VisionService class with provider abstraction
- [ ] Add OpenAI vision client integration
- [ ] Add Ollama local model integration
- [ ] Implement provider switching logic
- [ ] Add image preprocessing utilities

**Task 2.2: Implement Alt Text Generation**
- [ ] Create `generate_alt_text(image_url, context)` method
- [ ] Implement context-aware prompting with article metadata
- [ ] Add image download and format validation
- [ ] Handle image resizing for model compatibility
- [ ] Implement quality validation for generated alt text
- [ ] Add caching to avoid reprocessing identical images

**Task 2.3: Accessibility Standards Validation**
- [ ] Create `validate_alt_text_quality()` function
- [ ] Check character length (10-150 characters)
- [ ] Validate content quality (no generic phrases)
- [ ] Ensure contextual relevance to article
- [ ] Test against WCAG 2.1 guidelines
- [ ] Add improvement suggestions for failed validation

### Phase 3: Integration with Existing Workflow (3 hours)

**Task 3.1: Extend AI Service**
- [ ] **File**: `backend/services/ai_service.py`
- [ ] Import VisionService into existing AI service
- [ ] Add vision processing to `enrich_content()` method
- [ ] Handle image URL extraction from article content
- [ ] Implement fallback chain: OpenAI → Ollama → Manual requirement
- [ ] Add vision processing metrics to enrichment results

**Task 3.2: Update Article Schema**
- [ ] **File**: `backend/schemas/article.py`
- [ ] Add optional `image_urls` field for explicit image specification
- [ ] Modify alt text validation to accept generated content
- [ ] Update validation logic to trigger alt text generation
- [ ] Handle articles with multiple images
- [ ] Add validation for supported image formats

**Task 3.3: Update Main Application**
- [ ] **File**: `backend/main.py`
- [ ] Integrate vision processing into activation workflow
- [ ] Add vision model status to health check endpoint
- [ ] Update error handling for vision processing failures
- [ ] Add vision processing metrics to ActivationLog
- [ ] Ensure activation continues if vision models fail

### Phase 4: Prompting and Quality Control (2 hours)

**Task 4.1: Develop Context-Aware Prompts**
- [ ] Create comprehensive alt text generation prompt template
- [ ] Include article context (title, tags, audience) in prompts
- [ ] Test prompts with various image types and contexts
- [ ] Optimize prompts for both GPT-4o and Qwen models
- [ ] Add prompt versioning for A/B testing
- [ ] Document prompt engineering decisions

**Task 4.2: Implement Quality Validation**
- [ ] Create quality scoring system for generated alt text
- [ ] Set minimum quality thresholds for acceptance
- [ ] Add human review triggers for low-quality results
- [ ] Implement retry logic with prompt variations
- [ ] Log quality metrics for continuous improvement
- [ ] Add manual override capabilities

### Phase 5: Testing and Error Handling (3 hours)

**Task 5.1: Unit Testing**
- [ ] **File**: `backend/tests/test_vision_service.py` (new)
- [ ] Test VisionService initialization and provider switching
- [ ] Test image download and preprocessing
- [ ] Test alt text generation with mock responses
- [ ] Test quality validation functions
- [ ] Test error handling for various failure modes
- [ ] Mock external API calls for consistent testing

**Task 5.2: Integration Testing**
- [ ] Test complete activation flow with vision processing
- [ ] Test fallback from OpenAI to Ollama to manual requirement
- [ ] Test handling of articles with multiple images
- [ ] Test performance under various image sizes and types
- [ ] Test cost control and rate limiting mechanisms
- [ ] Verify accessibility compliance of generated content

**Task 5.3: Error Scenario Testing**
- [ ] Test behavior when OpenAI API unavailable
- [ ] Test behavior when Ollama service down
- [ ] Test handling of unsupported image formats
- [ ] Test timeout handling for large images
- [ ] Test network failures during image download
- [ ] Verify graceful degradation maintains activation flow

## Verification Methods

### Functional Testing
1. **Alt Text Generation**: Generate alt text for various image types
2. **Model Switching**: Test both OpenAI and Ollama models work correctly
3. **Quality Validation**: Verify generated alt text meets accessibility standards
4. **Context Awareness**: Confirm alt text reflects article topic and intent
5. **Error Handling**: Test graceful failure when vision models unavailable

### Performance Testing
1. **Processing Time**: Vision processing under performance targets
2. **Memory Usage**: Monitor RAM usage during local model processing
3. **API Usage**: Track OpenAI API calls and costs
4. **Cache Efficiency**: Measure cache hit rates for repeated images
5. **Throughput**: Handle multiple concurrent vision processing requests

### Accessibility Testing
1. **WCAG Compliance**: Validate generated alt text meets Level AA standards
2. **Screen Reader Testing**: Test alt text with actual screen reader software
3. **Content Quality**: Human evaluation of alt text descriptiveness
4. **Length Validation**: Ensure consistent 10-150 character compliance
5. **Context Relevance**: Verify marketing context appropriately reflected

## File Changes Required

```
backend/
├── services/
│   ├── vision_service.py         # New vision processing service
│   ├── ai_service.py             # Extended with vision integration
│   └── __init__.py               # Export VisionService
├── schemas/
│   └── article.py                # Updated with image_urls field
├── main.py                       # Vision integration in activation flow
├── requirements.txt              # Add ollama, Pillow dependencies
└── tests/
    ├── test_vision_service.py    # New vision service tests
    └── test_main.py              # Updated integration tests

.env.template                     # Add vision configuration
README.md                        # Document vision setup
```

## Configuration Examples

### OpenAI Vision Configuration
```bash
VISION_PROVIDER=openai
OPENAI_API_KEY=sk-proj-abc123...
MAX_IMAGE_SIZE_MB=10
VISION_PROCESSING_TIMEOUT=30
```

### Local Ollama Configuration
```bash
VISION_PROVIDER=local
OLLAMA_BASE_URL=http://localhost:11434
VISION_MODEL_NAME=qwen2.5vl:7b
MAX_IMAGE_SIZE_MB=10
VISION_PROCESSING_TIMEOUT=60
```

### Hybrid Configuration (Fallback Chain)
```bash
VISION_PROVIDER=openai
VISION_FALLBACK_PROVIDER=local
OPENAI_API_KEY=sk-proj-abc123...
OLLAMA_BASE_URL=http://localhost:11434
VISION_MODEL_NAME=qwen2.5vl:7b
```

## Success Criteria

### Technical Success
- [ ] Both OpenAI and Ollama vision models successfully integrated
- [ ] Alt text generated for 95%+ of articles with images
- [ ] Vision processing adds <3 seconds to activation time
- [ ] Generated alt text meets WCAG 2.1 Level AA standards
- [ ] Graceful fallback when vision models unavailable
- [ ] All existing tests continue to pass

### Quality Success
- [ ] 95%+ of generated alt text within 10-150 character range
- [ ] 90%+ context relevance based on article topic
- [ ] 85%+ human acceptance rate for generated alt text
- [ ] No generic phrases ("image of", "picture of") in results
- [ ] Consistent quality across different image types

### Performance Success
- [ ] OpenAI vision processing: <2 seconds per image (p95)
- [ ] Local Qwen processing: <5 seconds per image (p95)
- [ ] Memory usage stable during extended operation
- [ ] Cost controls prevent runaway OpenAI API usage
- [ ] Cache hit rate >20% for repeated image processing

## Implementation Notes

### Model Selection Guidelines
- **Use OpenAI GPT-4o when**: High quality required, budget allows, fast processing needed
- **Use Ollama Qwen when**: Cost control priority, privacy concerns, offline processing needed
- **Consider hybrid**: OpenAI for critical content, Ollama for bulk processing

### Image Processing Best Practices
- **Preprocessing**: Resize images >5MB to optimize processing time
- **Format Support**: Focus on JPEG, PNG, WebP - most common web formats
- **Caching Strategy**: Cache by image URL hash to handle duplicate images
- **Error Recovery**: Always provide path to continue activation without alt text

### Quality Assurance
- **Human Review**: Flag low-confidence results for manual review
- **Continuous Learning**: Log quality feedback for prompt improvement
- **A/B Testing**: Test different prompt variations for optimal results
- **Accessibility Focus**: Prioritize screen reader usability over marketing copy
