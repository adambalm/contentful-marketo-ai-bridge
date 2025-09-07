# Live Contentful Integration Tests

This is the tests coverage details for the spec detailed in @.agent-os/features/live-contentful-integration/spec.md

> Created: 2025-01-06
> Version: 1.0.0

## Test Coverage

### Unit Tests (backend/tests/test_contentful_service.py)

**ContentfulService Configuration Tests**
- `test_contentful_service_initialization_success()` - Valid tokens create client
- `test_contentful_service_initialization_missing_tokens()` - Error on missing tokens
- `test_contentful_service_environment_configuration()` - Custom environment support
- `test_contentful_service_connection_validation()` - Test connectivity on startup

**Article Retrieval Tests**
- `test_get_article_success()` - Successful article retrieval from real API
- `test_get_article_field_mapping()` - Correct field mapping from Contentful format
- `test_get_article_missing_optional_fields()` - Handle articles with missing optional fields
- `test_get_article_not_found()` - Proper error for non-existent article IDs
- `test_get_article_invalid_entry_id()` - Handle malformed entry IDs gracefully
- `test_get_article_network_error()` - Network failure handling with retries

**ActivationLog Creation Tests**
- `test_write_activation_log_success()` - Create log entry via Management API
- `test_write_activation_log_json_serialization()` - Complex objects serialize correctly
- `test_write_activation_log_reference_linking()` - Article reference field set correctly
- `test_write_activation_log_authentication_failure()` - Handle token permission errors
- `test_write_activation_log_rate_limited()` - Retry logic for rate limit errors
- `test_write_activation_log_fallback_to_jsonl()` - JSONL fallback when API down

**ActivationLog Retrieval Tests**
- `test_read_latest_activation_log_success()` - Find most recent log for article
- `test_read_latest_activation_log_none_found()` - Handle articles with no logs
- `test_read_latest_activation_log_pagination()` - Handle articles with many logs
- `test_read_latest_activation_log_sorting()` - Correct chronological ordering

### Integration Tests (backend/tests/test_contentful_integration.py)

**Real API Connection Tests**
- `test_real_contentful_connection()` - Connect to actual development space
- `test_content_type_verification()` - Verify Article and ActivationLog models exist
- `test_token_permissions()` - Management token has required create/read permissions
- `test_delivery_vs_management_api()` - Different tokens for read vs write operations

**End-to-End Workflow Tests**
- `test_complete_activation_with_real_contentful()` - Full workflow with real API
- `test_article_to_activationlog_reference()` - Verify reference linking works
- `test_multiple_activations_same_article()` - Handle multiple logs per article
- `test_activation_log_ui_visibility()` - Created logs visible in Contentful UI

**Error Handling Integration Tests**
- `test_contentful_api_unavailable()` - Graceful degradation when API down
- `test_invalid_space_configuration()` - Clear errors for space access issues
- `test_content_model_mismatch()` - Handle missing or changed content types
- `test_network_timeout_recovery()` - Retry logic for intermittent failures

**Performance Integration Tests**
- `test_article_retrieval_performance()` - Under 500ms for article fetch
- `test_activation_log_creation_performance()` - Under 1s for log creation
- `test_rate_limiting_compliance()` - No more than 10 requests/second
- `test_concurrent_activation_handling()` - Multiple simultaneous activations

### Mock Service Compatibility Tests

**Backward Compatibility Tests**
- `test_mock_service_still_works()` - Mock fallback when no tokens provided
- `test_api_contract_consistency()` - Same interface between mock and real service
- `test_response_format_compatibility()` - Real API matches expected response format
- `test_existing_tests_still_pass()` - All 23 existing tests continue working

### Configuration Tests (backend/tests/test_configuration.py)

**Environment Variable Tests**
- `test_required_environment_variables()` - Error when required vars missing
- `test_optional_environment_variables()` - Defaults work when optional vars missing
- `test_environment_variable_validation()` - Invalid values rejected with clear errors
- `test_space_id_format_validation()` - Valid Contentful space ID format

**Startup Validation Tests**
- `test_startup_contentful_validation()` - App startup validates Contentful config
- `test_health_check_includes_contentful()` - `/health` endpoint tests Contentful
- `test_configuration_error_messages()` - Clear, actionable error messages

## Mocking Requirements

### Development Mocking Strategy
```python
# Test environment detection
@pytest.fixture
def use_real_contentful():
    """Use real Contentful API when CONTENTFUL_TEST_SPACE_ID is set."""
    return os.getenv("CONTENTFUL_TEST_SPACE_ID") is not None

@pytest.fixture
def contentful_service(use_real_contentful):
    """Return real or mock service based on environment."""
    if use_real_contentful:
        return ContentfulService(
            space_id=os.getenv("CONTENTFUL_TEST_SPACE_ID"),
            management_token=os.getenv("CONTENTFUL_TEST_MANAGEMENT_TOKEN"),
            delivery_token=os.getenv("CONTENTFUL_TEST_DELIVERY_TOKEN")
        )
    else:
        return MockContentfulService()
```

### API Response Mocking
```python
# Mock Contentful API responses for unit tests
@pytest.fixture
def mock_contentful_article_response():
    return {
        "sys": {
            "id": "test-article-123",
            "type": "Entry",
            "contentType": {"sys": {"id": "article"}},
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-15T10:30:00Z"
        },
        "fields": {
            "title": "Test Article Title",
            "body": "Article body content with sufficient length...",
            "summary": "Article summary under 160 characters",
            "campaignTags": ["thought-leadership", "marketer", "awareness"],
            "hasImages": True,
            "altText": "Image description for accessibility",
            "ctaText": "Learn More",
            "ctaUrl": "https://example.com/learn-more"
        }
    }
```

### Error Scenario Mocking
```python
# Mock various Contentful API error conditions
@pytest.fixture
def mock_contentful_errors():
    return {
        "not_found": contentful.errors.NotFoundError("Entry not found"),
        "unauthorized": contentful.errors.UnauthorizedError("Invalid token"),
        "rate_limited": contentful.errors.RateLimitExceededError("Rate limit exceeded"),
        "network_error": requests.exceptions.ConnectionError("Network unreachable")
    }
```

## Test Data Setup

### Test Content Creation
```python
# Helper to create test articles in development space
def create_test_article(contentful_service, article_data):
    """Create test article for integration testing."""
    return contentful_service.management_client.entries(
        contentful_service.space_id,
        contentful_service.environment
    ).create(None, {
        'content_type_id': 'article',
        'fields': article_data
    })

# Standard test articles
TEST_ARTICLES = [
    {
        'title': {'en-US': 'Integration Test Article 1'},
        'body': {'en-US': 'Test article with all required fields and sufficient length for validation...'},
        'campaignTags': {'en-US': ['thought-leadership', 'developer', 'awareness']},
        'hasImages': {'en-US': True},
        'altText': {'en-US': 'Test image description'},
        'ctaText': {'en-US': 'Get Started'},
        'ctaUrl': {'en-US': 'https://example.com/get-started'}
    }
]
```

### Test Environment Setup
```bash
# Test-specific environment variables
CONTENTFUL_TEST_SPACE_ID=test_space_abc123
CONTENTFUL_TEST_MANAGEMENT_TOKEN=test_mgmt_token_xyz
CONTENTFUL_TEST_DELIVERY_TOKEN=test_delivery_token_xyz
CONTENTFUL_TEST_ENVIRONMENT=testing
```

## Performance Test Criteria

### Response Time Targets
- **Article Retrieval**: p95 < 500ms including network round trip
- **ActivationLog Creation**: p95 < 1000ms including content creation
- **Latest Log Retrieval**: p95 < 300ms with efficient querying
- **Configuration Validation**: < 100ms on application startup

### Rate Limiting Compliance
- **Request Rate**: Maximum 10 requests/second to Contentful APIs
- **Burst Handling**: Queue up to 50 requests, process at rate limit
- **Backoff Strategy**: Exponential backoff starting at 1s, max 30s
- **Error Recovery**: Resume normal operation after rate limit expires

### Concurrent Usage
- **Multiple Activations**: Handle 5 simultaneous activations without errors
- **Connection Pool**: Efficient connection reuse to minimize overhead
- **Memory Usage**: No memory leaks during sustained operation
- **Resource Cleanup**: Proper cleanup of HTTP connections and clients

## Success Metrics

### Functional Success
- [ ] 100% of real Contentful operations complete successfully in test environment
- [ ] All ActivationLogs visible in Contentful web UI after creation
- [ ] Graceful degradation maintains activation functionality when Contentful down
- [ ] Field mapping maintains 100% accuracy between API and application schemas

### Performance Success
- [ ] Article retrieval consistently under 500ms (p95)
- [ ] No rate limit violations during normal operation
- [ ] Zero degradation in existing activation performance
- [ ] Memory usage stable during extended operation

### Integration Success
- [ ] All 23 existing backend tests continue passing
- [ ] New integration tests achieve 90%+ coverage on Contentful service
- [ ] End-to-end workflow completes in under 5 seconds total
- [ ] Setup documentation enables successful configuration in under 15 minutes
