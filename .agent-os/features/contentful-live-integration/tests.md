# Contentful Live Integration Test Specification

This is the test coverage for Contentful Live Integration detailed in @.agent-os/features/contentful-live-integration/spec.md

> Created: 2025-09-06
> Version: 1.0.0
> Test Framework: pytest with async support
> Coverage Target: >95% of integration logic

## Test Coverage Matrix

### Unit Tests - ContentfulService Class

#### Authentication & Client Setup
- [ ] **test_contentful_service_initialization** - Proper client initialization with credentials
- [ ] **test_contentful_service_invalid_credentials** - Handle invalid API tokens gracefully
- [ ] **test_contentful_service_missing_credentials** - Validate required environment variables
- [ ] **test_contentful_service_client_configuration** - Verify delivery and management client setup

#### Content Retrieval Methods
- [ ] **test_get_article_success** - Successfully retrieve article with all fields
- [ ] **test_get_article_with_assets** - Retrieve article with linked images and proper CDN URLs
- [ ] **test_get_article_missing_entry** - Handle non-existent entry IDs gracefully
- [ ] **test_get_article_api_error** - Proper error handling for Contentful API failures
- [ ] **test_get_article_rate_limit** - Handle rate limiting with backoff strategy

#### Asset Processing
- [ ] **test_get_article_images_success** - Retrieve all linked images for an article
- [ ] **test_get_article_images_no_images** - Handle articles without images properly
- [ ] **test_get_article_images_missing_assets** - Handle missing or deleted asset references
- [ ] **test_resolve_asset_urls** - Properly resolve Contentful CDN URLs for images

#### Content Updates
- [ ] **test_update_article_alt_text** - Successfully update alt text in Contentful
- [ ] **test_update_article_metadata** - Update processing metadata fields
- [ ] **test_update_article_permissions** - Handle insufficient permissions for updates
- [ ] **test_update_article_concurrent_modification** - Handle concurrent update conflicts

### Integration Tests - Schema Mapping

#### ContentfulArticle to ArticleIn Mapping
- [ ] **test_contentful_to_articlein_mapping** - Complete field mapping validation
- [ ] **test_contentful_mapping_required_fields** - Ensure required fields are properly mapped
- [ ] **test_contentful_mapping_optional_fields** - Handle optional fields gracefully
- [ ] **test_contentful_mapping_validation_errors** - Proper validation error handling for invalid data

#### Data Type Conversions
- [ ] **test_contentful_rich_text_to_string** - Convert rich text fields to plain strings
- [ ] **test_contentful_asset_to_image_urls** - Convert asset references to image URLs
- [ ] **test_contentful_tags_to_campaign_tags** - Map Contentful tags to campaign tags
- [ ] **test_contentful_metadata_extraction** - Extract and map metadata fields properly

#### Backward Compatibility
- [ ] **test_mapping_backward_compatibility** - Ensure existing mock data still works
- [ ] **test_schema_evolution_compatibility** - Handle schema changes gracefully
- [ ] **test_mixed_content_sources** - Support both Contentful and mock content simultaneously

### Integration Tests - Activation Flow

#### Live Content Activation
- [ ] **test_activate_contentful_article_success** - Complete activation flow with live content
- [ ] **test_activate_contentful_article_with_images** - Vision processing with Contentful images
- [ ] **test_activate_contentful_article_validation** - Contentful content passes existing validation
- [ ] **test_activate_contentful_article_error_handling** - Proper error handling for activation failures

#### Content Processing Pipeline
- [ ] **test_contentful_content_ai_enrichment** - AI enrichment works with live content
- [ ] **test_contentful_content_brand_voice_analysis** - Brand voice analysis on live content
- [ ] **test_contentful_content_marketing_platform** - Send live content to marketing platforms
- [ ] **test_contentful_activation_log** - ActivationLog captures Contentful metadata

#### API Endpoint Integration
- [ ] **test_activate_endpoint_contentful_id** - Accept contentful_entry_id parameter
- [ ] **test_activate_endpoint_mixed_params** - Handle both contentful and direct content input
- [ ] **test_activate_endpoint_contentful_errors** - API error responses for Contentful failures
- [ ] **test_activate_endpoint_contentful_validation** - Validation errors with clear messages

### Performance Tests

#### API Response Times
- [ ] **test_contentful_retrieval_performance** - Content retrieval within 2-second requirement
- [ ] **test_contentful_batch_processing** - Performance with multiple concurrent requests
- [ ] **test_contentful_large_content_performance** - Performance with large articles and many images
- [ ] **test_contentful_cache_performance** - Caching improves response times appropriately

#### Rate Limiting & Resource Management
- [ ] **test_contentful_rate_limit_handling** - Proper backoff and retry for rate limits
- [ ] **test_contentful_concurrent_request_limits** - Handle multiple simultaneous API calls
- [ ] **test_contentful_memory_usage** - Memory usage remains within acceptable bounds
- [ ] **test_contentful_connection_pooling** - Efficient connection reuse for API calls

### Security Tests

#### Authentication Security
- [ ] **test_contentful_token_validation** - Validate API tokens before use
- [ ] **test_contentful_token_rotation** - Support for token rotation and refresh
- [ ] **test_contentful_environment_isolation** - Proper separation of dev/staging/prod environments
- [ ] **test_contentful_access_permissions** - Respect Contentful space access permissions

#### Data Security
- [ ] **test_contentful_data_sanitization** - Sanitize all incoming data from Contentful
- [ ] **test_contentful_error_message_security** - No sensitive data exposed in error messages
- [ ] **test_contentful_logging_security** - Secure logging without exposing credentials
- [ ] **test_contentful_webhook_signature_validation** - Validate webhook signatures properly

### Error Handling Tests

#### API Error Scenarios
- [ ] **test_contentful_network_timeout** - Handle network timeouts gracefully
- [ ] **test_contentful_service_unavailable** - Handle Contentful service outages
- [ ] **test_contentful_malformed_response** - Handle unexpected API response formats
- [ ] **test_contentful_quota_exceeded** - Handle API quota exhaustion scenarios

#### Content Error Scenarios
- [ ] **test_contentful_invalid_content_structure** - Handle unexpected content structures
- [ ] **test_contentful_missing_required_fields** - Handle content missing required fields
- [ ] **test_contentful_corrupted_assets** - Handle corrupted or inaccessible assets
- [ ] **test_contentful_unpublished_content** - Handle draft/unpublished content appropriately

#### Integration Error Scenarios
- [ ] **test_contentful_activation_partial_failure** - Handle partial activation failures
- [ ] **test_contentful_vision_processing_error** - Handle vision processing errors with live images
- [ ] **test_contentful_marketing_platform_error** - Handle marketing platform errors with live content
- [ ] **test_contentful_audit_log_failure** - Handle audit logging failures gracefully

## Mocking Requirements

### Contentful API Mocking
```python
# Mock Contentful API responses for testing
@pytest.fixture
def mock_contentful_entry():
    return {
        'sys': {'id': 'test-entry-id', 'type': 'Entry'},
        'fields': {
            'title': {'en-US': 'Test Article Title'},
            'body': {'en-US': 'Test article body content'},
            'campaignTags': {'en-US': ['lead-generation', 'b2b', 'enterprise']},
            'images': {
                'en-US': [
                    {'sys': {'id': 'asset1', 'type': 'Link', 'linkType': 'Asset'}}
                ]
            }
        }
    }

@pytest.fixture
def mock_contentful_asset():
    return {
        'sys': {'id': 'asset1', 'type': 'Asset'},
        'fields': {
            'title': {'en-US': 'Test Image'},
            'file': {
                'en-US': {
                    'url': '//images.ctfassets.net/example/test-image.jpg',
                    'contentType': 'image/jpeg'
                }
            }
        }
    }
```

### Contentful SDK Mocking
```python
# Mock contentful SDK clients for testing
@pytest.fixture
def mock_contentful_client():
    with patch('contentful.Client') as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_contentful_management_client():
    with patch('contentful_management.Client') as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        yield mock_instance
```

### Error Scenario Mocking
```python
# Mock various error conditions
@pytest.fixture
def mock_contentful_api_error():
    return contentful.errors.NotFoundError("Entry not found")

@pytest.fixture
def mock_contentful_rate_limit_error():
    return contentful.errors.RateLimitExceededError("Rate limit exceeded")
```

## Test Environment Configuration

### Environment Variables for Testing
```bash
# Test-specific Contentful configuration
CONTENTFUL_SPACE_ID=test_space_id
CONTENTFUL_DELIVERY_TOKEN=test_delivery_token
CONTENTFUL_MANAGEMENT_TOKEN=test_management_token
CONTENTFUL_ENVIRONMENT=test
CONTENTFUL_API_BASE_URL=https://cdn.contentful.com  # For mocking override
```

### Test Data Requirements
- **Sample Content Models**: Article content type with all required fields
- **Test Entries**: 5+ sample articles with varying content and image configurations
- **Test Assets**: Sample images for vision processing and CDN URL testing
- **Error Test Cases**: Predefined error scenarios for comprehensive testing

## Testing Strategy by Phase

### Phase 2.1: Basic Integration Testing
- **Priority**: API integration and schema mapping tests
- **Coverage**: Core ContentfulService methods and basic activation flow
- **Mocking**: Heavy use of Contentful API mocks for reliable testing
- **Performance**: Basic response time validation

### Phase 2.2: Enhanced Integration Testing
- **Priority**: Webhook processing and real-time synchronization
- **Coverage**: Advanced error scenarios and performance optimization
- **Integration**: More live API testing with dedicated test space
- **Monitoring**: Performance benchmarking and load testing

### Continuous Integration Integration

#### Test Execution Strategy
- **Mock-First Testing**: Primary test suite uses mocks for speed and reliability
- **Integration Test Suite**: Separate suite for actual Contentful API testing
- **Environment Separation**: Different test configurations for different environments
- **Performance Monitoring**: Track test execution times and API response benchmarks

#### Quality Gates
- All Contentful integration tests must pass before merge
- Performance tests validate 2-second response time requirement
- Security tests ensure no credential exposure or data leaks
- Coverage requirement: >95% of Contentful integration logic

## Coverage Metrics & Quality Standards

### Current Test Coverage Goals
- **ContentfulService Class**: 100% line coverage for all methods
- **Schema Mapping**: 100% coverage for all mapping scenarios
- **Integration Flow**: 95% coverage including error scenarios
- **Error Handling**: 100% coverage for all defined error types
- **Security**: 100% coverage for authentication and data security

### Quality Assurance Standards
- All tests must be deterministic and not dependent on external state
- Error scenarios must be comprehensively tested with proper mocking
- Performance tests must validate real-world usage patterns
- Security tests must cover all authentication and authorization scenarios
- Integration tests must maintain backward compatibility with existing features
