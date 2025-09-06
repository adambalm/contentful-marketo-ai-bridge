# Vision Alt Text Generation Tests

This is the tests coverage details for the spec detailed in @.agent-os/features/vision-alt-text-generation/spec.md

> Created: 2025-01-06
> Version: 1.0.0

## Test Coverage

### Unit Tests (backend/tests/test_vision_service.py)

**VisionService Initialization Tests**
- `test_vision_service_openai_provider()` - OpenAI provider initialization with valid API key
- `test_vision_service_local_provider()` - Local Ollama provider initialization
- `test_vision_service_invalid_provider()` - Error handling for unsupported providers
- `test_vision_service_missing_credentials()` - Error when API keys/endpoints missing
- `test_vision_service_provider_switching()` - Dynamic switching between providers

**Image Processing Tests**
- `test_image_download_success()` - Download images from valid URLs
- `test_image_download_invalid_url()` - Handle malformed or inaccessible URLs
- `test_image_format_validation()` - Accept JPEG, PNG, WebP; reject unsupported formats
- `test_image_size_validation()` - Enforce maximum file size limits (10MB)
- `test_image_preprocessing()` - Resize oversized images for model compatibility
- `test_image_caching()` - Cache downloaded images to avoid repeated fetching

**Alt Text Generation Tests**
- `test_generate_alt_text_openai()` - OpenAI GPT-4o vision model integration
- `test_generate_alt_text_local()` - Ollama Qwen 2.5VL model integration
- `test_context_aware_prompting()` - Include article context in prompts
- `test_alt_text_length_compliance()` - Generated text within 10-150 characters
- `test_alt_text_quality_standards()` - No generic phrases, descriptive content
- `test_multiple_image_handling()` - Process articles with multiple images

**Quality Validation Tests**
- `test_validate_alt_text_quality()` - Quality scoring algorithm accuracy
- `test_accessibility_compliance()` - WCAG 2.1 Level AA standards checking
- `test_context_relevance_scoring()` - Relevance to article topic and tags
- `test_generic_phrase_detection()` - Identify and reject generic alt text
- `test_character_length_validation()` - Enforce 10-150 character limits
- `test_human_readability_metrics()` - Screen reader compatibility scoring

**Error Handling Tests**
- `test_openai_api_failure()` - Handle OpenAI API outages gracefully
- `test_ollama_service_down()` - Handle Ollama service unavailability
- `test_image_download_timeout()` - Handle slow or failed image downloads
- `test_model_processing_timeout()` - Handle vision model processing timeouts
- `test_network_connectivity_issues()` - Handle network failures during processing
- `test_invalid_api_responses()` - Handle malformed responses from vision models

### Integration Tests (backend/tests/test_vision_integration.py)

**End-to-End Workflow Tests**
- `test_complete_activation_with_vision()` - Full activation workflow with alt text generation
- `test_article_with_multiple_images()` - Handle articles containing multiple images
- `test_vision_fallback_chain()` - OpenAI → Ollama → Manual requirement fallback
- `test_existing_alt_text_preservation()` - Preserve manually provided alt text
- `test_vision_processing_in_enrichment()` - Integration with AI enrichment pipeline

**Provider Switching Tests**
- `test_openai_to_ollama_fallback()` - Automatic fallback when OpenAI fails
- `test_provider_performance_comparison()` - Compare OpenAI vs Ollama quality/speed
- `test_hybrid_configuration()` - Mix of OpenAI and Ollama based on conditions
- `test_cost_control_switching()` - Switch providers based on usage limits

**Performance Integration Tests**
- `test_vision_processing_latency()` - Vision processing under 3 seconds target
- `test_concurrent_vision_processing()` - Multiple simultaneous image processing
- `test_memory_usage_under_load()` - Monitor memory during extended processing
- `test_cache_efficiency()` - Measure cache hit rates and performance impact

**Error Recovery Integration Tests**
- `test_vision_failure_continues_activation()` - Activation continues without vision
- `test_partial_vision_success()` - Handle some images processed, some failed
- `test_degraded_mode_operation()` - Operation when all vision models unavailable
- `test_configuration_error_handling()` - Clear errors for misconfiguration

### Accessibility Tests (backend/tests/test_accessibility.py)

**WCAG Compliance Tests**
- `test_wcag_level_aa_compliance()` - Generated alt text meets Level AA standards
- `test_screen_reader_compatibility()` - Alt text readable by screen reader software
- `test_context_appropriateness()` - Alt text appropriate for marketing context
- `test_informative_vs_decorative()` - Distinguish informative from decorative images
- `test_complex_image_descriptions()` - Handle charts, diagrams, UI screenshots

**Content Quality Tests**
- `test_descriptive_accuracy()` - Alt text accurately describes visual content
- `test_context_relevance()` - Alt text relates to article topic and purpose
- `test_conciseness_vs_completeness()` - Balance between brevity and information
- `test_technical_accuracy()` - Correct identification of UI elements, brands, etc.
- `test_audience_appropriateness()` - Alt text matches intended audience level

### Performance Tests (backend/tests/test_vision_performance.py)

**Response Time Tests**
- `test_openai_vision_response_time()` - OpenAI processing under 2 seconds (p95)
- `test_ollama_vision_response_time()` - Ollama processing under 5 seconds (p95)
- `test_image_download_speed()` - Image fetch under 1 second for <5MB files
- `test_end_to_end_latency()` - Complete vision pipeline under 3 seconds
- `test_cache_performance_impact()` - Cache hit vs miss response time difference

**Resource Usage Tests**
- `test_memory_consumption()` - Memory usage during local model processing
- `test_gpu_utilization()` - GPU usage when available for local models
- `test_cpu_usage_patterns()` - CPU usage during image preprocessing
- `test_network_bandwidth()` - Bandwidth usage for API calls and image downloads
- `test_disk_space_usage()` - Storage usage for image caching and models

**Scalability Tests**
- `test_concurrent_processing_limit()` - Maximum simultaneous vision requests
- `test_queue_management()` - Request queuing during high load
- `test_rate_limit_handling()` - Respect OpenAI API rate limits
- `test_batch_processing_efficiency()` - Multiple images in single article

### Cost Control Tests (backend/tests/test_cost_management.py)

**Usage Monitoring Tests**
- `test_openai_api_usage_tracking()` - Track API calls and estimated costs
- `test_daily_usage_limits()` - Enforce configurable daily spending limits  
- `test_monthly_budget_controls()` - Monthly budget tracking and limits
- `test_cost_per_activation_metrics()` - Calculate cost per activation with vision
- `test_usage_reporting()` - Generate usage reports for cost analysis

**Optimization Tests**
- `test_cache_cost_savings()` - Measure cost reduction from image caching
- `test_model_selection_optimization()` - Choose models based on cost/quality tradeoffs
- `test_image_preprocessing_savings()` - Cost reduction from image optimization
- `test_batch_processing_economies()` - Cost efficiency of batch processing

## Mocking Requirements

### Vision Model Mocking
```python
@pytest.fixture
def mock_openai_vision():
    """Mock OpenAI GPT-4o Vision API responses."""
    with patch('openai.OpenAI') as mock_client:
        mock_client.return_value.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Marketing dashboard showing analytics data"))]
        )
        yield mock_client

@pytest.fixture
def mock_ollama_vision():
    """Mock Ollama local vision model responses."""
    with patch('ollama.chat') as mock_chat:
        mock_chat.return_value = {
            'message': {
                'content': 'Software interface displaying marketing metrics and charts'
            }
        }
        yield mock_chat
```

### Image Processing Mocking
```python
@pytest.fixture
def mock_image_download():
    """Mock image download for testing without external dependencies."""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'fake_image_data'
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def sample_test_images():
    """Provide test image URLs and expected alt text for validation."""
    return {
        'dashboard_screenshot': {
            'url': 'https://example.com/dashboard.png',
            'expected_alt': 'Marketing dashboard showing analytics data',
            'context': {'title': 'Analytics Guide', 'tags': ['analytics', 'dashboard']}
        },
        'product_photo': {
            'url': 'https://example.com/product.jpg', 
            'expected_alt': 'Content management interface with editing tools',
            'context': {'title': 'CMS Features', 'tags': ['product', 'cms']}
        }
    }
```

### Quality Assessment Mocking
```python
@pytest.fixture
def accessibility_validator():
    """Mock accessibility validation for consistent testing."""
    def validate(alt_text):
        return {
            'length_valid': 10 <= len(alt_text) <= 150,
            'descriptive': len(alt_text.split()) >= 3,
            'not_generic': not alt_text.lower().startswith(('image of', 'picture of')),
            'wcag_compliant': True,
            'score': 0.85
        }
    return validate
```

## Test Data Management

### Image Test Assets
```python
# Test image URLs for different scenarios
TEST_IMAGES = {
    'valid_jpeg': 'https://via.placeholder.com/800x600.jpg',
    'valid_png': 'https://via.placeholder.com/800x600.png',
    'oversized': 'https://example.com/large_image_15mb.jpg',  # >10MB
    'invalid_format': 'https://example.com/document.pdf',
    'broken_url': 'https://nonexistent.com/missing.jpg',
    'slow_response': 'https://httpbin.org/delay/5',  # Timeout testing
}

# Expected alt text for quality validation
EXPECTED_ALT_TEXT = {
    'dashboard': 'Analytics dashboard displaying marketing performance metrics',
    'product_ui': 'Content management interface with editing and publishing tools',
    'chart': 'Bar chart showing monthly user growth trends',
    'team_photo': 'Marketing team collaborating in modern office environment',
}
```

### Context Scenarios
```python
# Article contexts for testing contextual alt text generation
TEST_CONTEXTS = [
    {
        'title': 'Marketing Analytics Deep Dive',
        'campaign_tags': ['analytics', 'marketer', 'awareness'],
        'content_type': 'thought-leadership',
        'target_audience': 'marketer'
    },
    {
        'title': 'Developer API Documentation',
        'campaign_tags': ['developer', 'tutorial', 'technical'],
        'content_type': 'documentation',  
        'target_audience': 'developer'
    },
    {
        'title': 'Enterprise Solution Overview',
        'campaign_tags': ['enterprise', 'product-launch', 'decision'],
        'content_type': 'product-overview',
        'target_audience': 'executive'
    }
]
```

## Performance Benchmarks

### Response Time Targets
- **OpenAI GPT-4o**: <2000ms per image (p95)
- **Ollama Qwen 2.5VL**: <5000ms per image (p95, CPU) / <2000ms (GPU)
- **Image Download**: <1000ms for images <5MB
- **Quality Validation**: <100ms per alt text string
- **Cache Retrieval**: <50ms for cached results

### Resource Usage Limits
- **Memory Usage**: <2GB additional during local model processing
- **CPU Usage**: <80% sustained during vision processing
- **Network Bandwidth**: <100MB/hour for typical usage patterns
- **Disk Cache**: <1GB for image cache storage
- **API Quota**: <1000 OpenAI vision requests per day (configurable)

### Quality Thresholds
- **Accessibility Score**: >0.8 for generated alt text
- **Context Relevance**: >0.75 based on article topic matching
- **Character Length**: 95%+ within 10-150 character range
- **Generic Phrase Rate**: <5% containing "image of", "picture of"
- **Human Approval Rate**: >85% acceptable without editing

## Success Metrics

### Functional Success
- [ ] 95%+ of articles with images receive generated alt text
- [ ] Both OpenAI and Ollama models process images successfully  
- [ ] Generated alt text meets WCAG 2.1 Level AA standards
- [ ] Vision processing integrates seamlessly with activation workflow
- [ ] Graceful degradation when vision models unavailable

### Performance Success
- [ ] Vision processing adds <3 seconds to activation time
- [ ] Memory usage remains stable during extended operation
- [ ] Cache hit rate >20% reducing redundant processing
- [ ] No degradation in existing activation performance
- [ ] Cost controls prevent runaway API usage

### Quality Success
- [ ] 90%+ context relevance based on article topic
- [ ] 85%+ human acceptance rate for generated alt text
- [ ] 95%+ character length compliance (10-150 chars)
- [ ] <5% generic phrase usage in generated content
- [ ] Consistent quality across different image types and contexts

## Integration with Existing Tests

### Test Suite Updates Required
```python
# Update existing activation tests to handle vision processing
def test_activate_with_vision_enabled(client, article_with_images):
    """Ensure existing activation tests work with vision enabled."""
    pass

def test_activate_with_vision_disabled(client, article_with_images):
    """Ensure activation works when vision processing disabled.""" 
    pass

def test_existing_alt_text_preserved(client, article_with_alt_text):
    """Don't override manually provided alt text."""
    pass
```

### Backward Compatibility Verification
- All existing 23 backend tests must continue passing
- No changes to existing API contracts or response formats
- Vision features optional and disabled by default in test environment
- Existing mock services work unchanged when vision disabled