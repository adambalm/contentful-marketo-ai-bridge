# Live Contentful Integration Tasks

These are the tasks to be completed for the spec detailed in @.agent-os/features/live-contentful-integration/spec.md

> Created: 2025-01-06
> Status: Ready for Implementation

## Tasks

### Phase 1: Setup and Dependencies (2 hours)

**Task 1.1: Install Contentful SDKs**
- [ ] Add `contentful-management>=3.0.0` to backend/requirements.txt
- [ ] Add `contentful>=1.13.0` to backend/requirements.txt
- [ ] Update virtual environment: `pip install -r requirements.txt`
- [ ] Verify imports work in Python environment

**Task 1.2: Environment Configuration**
- [ ] Add Contentful variables to `.env.template`:
  ```bash
  CONTENTFUL_SPACE_ID=your_space_id_here
  CONTENTFUL_MANAGEMENT_TOKEN=your_management_token_here  
  CONTENTFUL_DELIVERY_TOKEN=your_delivery_token_here
  CONTENTFUL_ENVIRONMENT=master
  ```
- [ ] Update `.env.example` with same variables
- [ ] Document token acquisition process in README

**Task 1.3: Create Development Contentful Space**
- [ ] Create free Contentful account if needed
- [ ] Create development space for testing
- [ ] Generate management token with content creation permissions
- [ ] Generate delivery token for content reading
- [ ] Test token connectivity using Contentful's API explorer

### Phase 2: Content Model Setup (1.5 hours)

**Task 2.1: Create Article Content Type**
- [ ] Define Article content type in Contentful with fields:
  - title (Short text, required)
  - body (Long text, required) 
  - summary (Short text, optional)
  - campaignTags (Tags, required)
  - hasImages (Boolean, default false)
  - altText (Short text, optional)
  - ctaText (Short text, optional)
  - ctaUrl (Short text, optional)
- [ ] Publish Article content type
- [ ] Create 2-3 test articles for development

**Task 2.2: Create ActivationLog Content Type**
- [ ] Define ActivationLog content type with fields:
  - article_reference (Reference to Article)
  - activation_timestamp (Date and time)
  - ai_outputs (JSON object)
  - validation_results (JSON object)
  - marketo_response (JSON object)  
  - status (Select: draft, processing, completed, failed)
  - brand_voice_analysis (JSON object)
- [ ] Publish ActivationLog content type
- [ ] Test manual entry creation

### Phase 3: Service Implementation (4 hours)

**Task 3.1: Replace Mock ContentfulService**
- [ ] **File**: `backend/services/contentful.py`
- [ ] Import real Contentful SDKs:
  ```python
  from contentful import Client as DeliveryClient
  from contentful_management import Client as ManagementClient
  ```
- [ ] Replace `__init__()` method with real client initialization
- [ ] Add environment variable validation
- [ ] Add connection testing methods

**Task 3.2: Implement Real Article Retrieval**
- [ ] Replace `get_article()` method with Delivery API call
- [ ] Map Contentful response to expected format
- [ ] Handle field name variations (camelCase vs snake_case)
- [ ] Add error handling for missing entries
- [ ] Add caching for frequently accessed articles

**Task 3.3: Implement Real ActivationLog Creation**
- [ ] Replace `write_activation_log()` with Management API call
- [ ] Create entries using ActivationLog content type
- [ ] Handle JSON field serialization
- [ ] Add reference linking to source article
- [ ] Implement retry logic for API timeouts

**Task 3.4: Implement ActivationLog Retrieval**
- [ ] Replace `read_latest_activation_log()` with real query
- [ ] Use Delivery API to find logs by article reference
- [ ] Sort by creation date to get latest
- [ ] Handle pagination for articles with many logs
- [ ] Cache recent logs for performance

### Phase 4: Integration and Testing (3 hours)

**Task 4.1: Update Main Application**
- [ ] **File**: `backend/main.py`
- [ ] Add startup validation for Contentful configuration
- [ ] Update error handling for Contentful API failures
- [ ] Implement graceful degradation to JSONL when Contentful down
- [ ] Add health check endpoint for Contentful connectivity

**Task 4.2: Configuration Validation**
- [ ] Create `validate_contentful_config()` function
- [ ] Test space access with provided tokens
- [ ] Verify content types exist
- [ ] Check required permissions (read/write)
- [ ] Return clear error messages for misconfigurations

**Task 4.3: Rate Limiting Implementation**
- [ ] Add request throttling to respect 10 requests/second limit
- [ ] Implement exponential backoff for rate limit errors
- [ ] Queue requests during high-traffic periods
- [ ] Add metrics for API usage monitoring

### Phase 5: Testing (2 hours)

**Task 5.1: Update Existing Tests**
- [ ] **File**: `backend/tests/test_main.py`
- [ ] Update mocking to work with real ContentfulService
- [ ] Add tests for Contentful connection failures
- [ ] Test graceful degradation to JSONL logging
- [ ] Verify existing functionality still works

**Task 5.2: Add Integration Tests**
- [ ] Create `backend/tests/test_contentful_integration.py`
- [ ] Test real API connections (with test tokens)
- [ ] Test article retrieval from development space
- [ ] Test ActivationLog creation and retrieval
- [ ] Test field mapping accuracy
- [ ] Test rate limiting behavior

**Task 5.3: Error Scenario Testing**
- [ ] Test behavior with invalid tokens
- [ ] Test missing content type scenarios
- [ ] Test network timeout handling
- [ ] Test malformed API responses
- [ ] Verify fallback to JSONL logging works

## Verification Methods

### Functional Testing
1. **Article Retrieval**: Fetch real article from Contentful space
2. **ActivationLog Creation**: Create log entry and verify in Contentful UI
3. **Error Recovery**: Disconnect from Contentful and verify JSONL fallback
4. **Rate Limiting**: Send burst of requests and verify throttling

### Integration Testing  
1. **End-to-End**: Complete activation flow using real Contentful data
2. **Content Model**: Verify all required fields map correctly
3. **Authentication**: Test with various token permission levels
4. **Environment**: Test across different Contentful environments

### Performance Testing
1. **Response Time**: Article retrieval under 500ms (95th percentile)
2. **Log Creation**: ActivationLog creation under 1 second
3. **Rate Limiting**: No more than 10 requests per second to Contentful
4. **Error Handling**: Graceful degradation under 100ms

## File Changes Required

```
backend/
├── services/contentful.py     # Complete rewrite with real API
├── main.py                    # Add config validation, error handling
├── requirements.txt           # Add contentful SDKs
└── tests/
    ├── test_main.py          # Update mocking strategy
    └── test_contentful_integration.py  # New integration tests

.env.template                  # Add Contentful configuration
README.md                     # Document setup process
```

## Success Criteria

- [ ] Real articles retrieved from Contentful space
- [ ] ActivationLogs created as Contentful entries (visible in UI)
- [ ] All 23 existing backend tests still pass
- [ ] New integration tests verify real API functionality
- [ ] Graceful degradation when Contentful unavailable
- [ ] Clear setup documentation for new environments
- [ ] No impact on activation performance (still under 5 seconds)