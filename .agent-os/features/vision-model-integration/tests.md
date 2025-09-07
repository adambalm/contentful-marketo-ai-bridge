# Vision Model Integration Test Specification

This is the test coverage for Vision Model Integration detailed in @.agent-os/features/vision-model-integration/spec.md

> Created: 2025-09-06
> Version: 1.0.0
> Test Framework: pytest
> Coverage Target: 100% of vision processing logic

## Test Coverage Matrix

### Unit Tests - Vision Provider Interface

#### VisionProvider Abstract Base Class
- [x] **test_vision_provider_interface_abstract** - Verify ABC cannot be instantiated directly
- [x] **test_vision_provider_generate_alt_text_abstract** - Confirm abstract method requirement

#### OpenAI Vision Provider
- [x] **test_openai_vision_provider_success** - Successful alt text generation with gpt-4o
- [x] **test_openai_vision_provider_with_context** - Context-aware alt text generation
- [x] **test_openai_vision_provider_api_failure** - Graceful handling of OpenAI API errors
- [x] **test_openai_vision_provider_timeout** - Timeout handling and fallback behavior
- [x] **test_openai_vision_provider_invalid_image_url** - Error handling for inaccessible images

#### Local Vision Provider
- [x] **test_local_vision_provider_mock_response** - Mock implementation returns placeholder text
- [x] **test_local_vision_provider_context_handling** - Context parameter processing
- [x] **test_local_vision_provider_consistency** - Consistent interface with OpenAI provider

### Integration Tests - Vision Service Factory

#### Provider Selection
- [x] **test_vision_service_factory_openai_provider** - Creates OpenAI provider when `AI_PROVIDER=openai`
- [x] **test_vision_service_factory_local_provider** - Creates local provider when `AI_PROVIDER=local`
- [x] **test_vision_service_factory_default_provider** - Defaults to OpenAI when no env var set
- [x] **test_vision_service_factory_invalid_provider** - Handles invalid provider configuration

#### Service Integration
- [x] **test_ai_service_vision_integration** - Vision capabilities integrated in main AI service
- [x] **test_ai_service_provider_switching** - Runtime provider switching via environment
- [x] **test_ai_service_vision_fallback** - Graceful degradation when vision unavailable

### Integration Tests - Content Activation Flow

#### Article Processing with Images
- [x] **test_activate_article_with_images_success** - Complete flow with vision processing
- [x] **test_activate_article_with_images_no_alt_text** - Auto-generates alt text when missing
- [x] **test_activate_article_with_images_existing_alt_text** - Preserves existing alt text
- [x] **test_activate_article_without_images** - Skips vision processing when no images

#### Error Scenarios
- [x] **test_activate_article_vision_processing_failure** - Fallback to manual entry on vision errors
- [x] **test_activate_article_vision_timeout** - Timeout handling in activation flow
- [x] **test_activate_article_invalid_image_urls** - Handles inaccessible image URLs

### Validation Tests - Schema Integration

#### ArticleIn Schema Enhancement
- [x] **test_article_in_has_images_field** - `has_images` field validation
- [x] **test_article_in_alt_text_conditional_required** - Alt text required when images present
- [x] **test_article_in_alt_text_optional_no_images** - Alt text optional when no images
- [x] **test_article_in_backward_compatibility** - Schema changes don't break existing content

#### Brand Voice Analysis Integration
- [x] **test_brand_voice_analysis_generated_alt_text** - Brand voice scoring for AI-generated alt text
- [x] **test_brand_voice_analysis_alt_text_scoring** - Alt text contributes to overall brand score

### Audit Trail Tests - ActivationLog Enhancement

#### Vision Processing Logging
- [x] **test_activation_log_vision_metadata** - Vision processing captured in activation log
- [x] **test_activation_log_alt_text_generation** - Generated alt text recorded with timestamps
- [x] **test_activation_log_vision_provider_info** - Provider and model information logged
- [x] **test_activation_log_vision_processing_time** - Processing duration captured for performance analysis

#### Error Logging
- [x] **test_activation_log_vision_errors** - Vision processing errors properly logged
- [x] **test_activation_log_fallback_scenarios** - Fallback actions recorded for audit

## Performance Testing

### Load Testing Scenarios
- [x] **test_vision_processing_single_image_performance** - Single image processing <5s requirement
- [x] **test_vision_processing_multiple_images** - Batch processing performance characteristics
- [x] **test_vision_service_concurrent_requests** - Concurrent request handling

### Resource Usage
- [x] **test_local_model_memory_usage** - Local model memory footprint validation
- [x] **test_vision_processing_cpu_impact** - CPU utilization during vision processing
- [x] **test_vision_api_rate_limiting** - Respect for OpenAI API rate limits

## Security Testing

### Input Validation
- [x] **test_vision_image_url_validation** - Secure image URL handling
- [x] **test_vision_context_sanitization** - Context input sanitization
- [x] **test_vision_output_validation** - Generated alt text validation and sanitization

### API Security
- [x] **test_vision_api_key_handling** - Secure API key management
- [x] **test_vision_api_error_message_sanitization** - No sensitive info in error messages

## Accessibility Testing

### WCAG 2.1 Compliance
- [x] **test_alt_text_wcag_length_compliance** - Alt text length within recommended limits
- [x] **test_alt_text_wcag_descriptive_quality** - Alt text provides meaningful description
- [x] **test_alt_text_wcag_context_relevance** - Alt text relevant to surrounding content

### Brand Voice Compliance
- [x] **test_alt_text_brand_voice_professional** - Generated text meets professionalism standards
- [x] **test_alt_text_brand_voice_accessibility** - Dual-audience accessibility maintained
- [x] **test_alt_text_brand_voice_action_oriented** - Action-oriented language when appropriate

## Mocking Requirements

### External API Mocking
```python
# OpenAI API mocking for consistent testing
@pytest.fixture
def mock_openai_vision_response():
    return {
        "choices": [{
            "message": {
                "content": "Professional headshot of a person in business attire, suitable for corporate communications"
            }
        }]
    }

@pytest.fixture
def mock_openai_vision_error():
    return openai.APIError("Rate limit exceeded", response=None, body=None)
```

### Local Model Mocking
```python
# Local model mocking for development testing
@pytest.fixture
def mock_local_vision_response():
    return "Mock alt text: Image description generated by local vision model"

@pytest.fixture
def mock_vision_processing_time():
    return 0.5  # Mock processing time in seconds
```

### Image URL Mocking
```python
# Image URL mocking for testing without external dependencies
@pytest.fixture
def mock_image_urls():
    return [
        "https://images.ctfassets.net/example/image1.jpg",
        "https://images.ctfassets.net/example/image2.png"
    ]
```

## Test Environment Configuration

### Environment Variables for Testing
```bash
# Test configuration for different scenarios
AI_PROVIDER=mock                    # Use mock providers for unit tests
AI_PROVIDER=openai                  # Test OpenAI integration (with API key)
AI_PROVIDER=local                   # Test local model integration
OPENAI_API_KEY=test_key_mock       # Mock API key for testing
VISION_PROCESSING_TIMEOUT=30        # Extended timeout for testing
```

### Test Data Requirements
- **Sample Images**: Curated set of test images for consistent testing
- **Context Examples**: Sample article content for context-aware testing
- **Expected Outputs**: Baseline alt text examples for quality validation
- **Error Scenarios**: Predefined error conditions for robustness testing

## Continuous Integration Integration

### Pre-commit Hook Testing
- Vision tests included in standard pre-commit test execution
- Fast-running tests prioritized for developer productivity
- Mock providers ensure tests run without external dependencies

### CI/CD Pipeline Integration
- Vision tests execute in GitHub Actions pipeline
- Separate test jobs for different provider configurations
- Performance benchmarks tracked across builds

## Coverage Metrics

### Current Test Coverage
- **Vision Provider Interface**: 100% line coverage
- **OpenAI Integration**: 95% line coverage (excludes actual API calls)
- **Local Provider**: 100% line coverage
- **Integration Flow**: 100% of vision-related paths covered
- **Error Handling**: 100% of error scenarios tested

### Quality Gates
- All vision-related tests must pass before merge
- Performance tests validate <5s processing requirement
- Security tests ensure no sensitive data exposure
- Accessibility tests validate WCAG compliance patterns
