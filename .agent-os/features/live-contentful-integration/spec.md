# Live Contentful Integration Feature Spec

> Spec: live-contentful-integration
> Created: 2025-01-06
> Status: Planning

## Overview

Replace the mock ContentfulService with real Contentful Management and Delivery API integration. This feature enables the MVP to connect to actual Contentful spaces, retrieve real content, and create authentic ActivationLog entries within Contentful.

## Technical Requirements

### Contentful Management API Integration
- **Requirement**: Replace mock `ContentfulService.get_article()` with real CMA/CDA calls
- **API**: Contentful Management API v1 and Delivery API v2
- **Authentication**: Management token for write operations, delivery token for read operations
- **Content Model**: Support existing article content type with fields: title, body, summary, campaignTags, hasImages, altText, ctaText, ctaUrl

### ActivationLog Content Type
- **Requirement**: Create ActivationLog entries as actual Contentful entries
- **Fields**: 
  - `article_reference` (Reference to original article)
  - `activation_timestamp` (DateTime)
  - `ai_outputs` (JSON object)
  - `validation_results` (JSON object) 
  - `marketo_response` (JSON object)
  - `status` (Select: draft, processing, completed, failed)
  - `brand_voice_analysis` (JSON object)

### Environment Configuration
- **Space ID**: `CONTENTFUL_SPACE_ID` environment variable
- **Management Token**: `CONTENTFUL_MANAGEMENT_TOKEN` for write operations
- **Delivery Token**: `CONTENTFUL_DELIVERY_TOKEN` for read operations
- **Environment**: `CONTENTFUL_ENVIRONMENT` (defaults to 'master')

### Error Handling
- **Connection Failures**: Graceful degradation to JSONL logging when Contentful unavailable
- **Rate Limiting**: Respect Contentful API rate limits (10 requests/second)
- **Authentication Errors**: Clear error messages for token issues
- **Content Model Mismatches**: Validation and mapping for field variations

## Acceptance Criteria

1. **Real Content Retrieval**: Replace mock article data with actual Contentful entries
2. **ActivationLog Creation**: Create real Contentful entries for activation logs
3. **Authentication**: Successful connection using management/delivery tokens
4. **Field Mapping**: Correctly map Contentful fields to ArticleIn schema
5. **Error Recovery**: Fallback to JSONL logging when Contentful unavailable
6. **Rate Limiting**: Implement request throttling to stay within API limits
7. **Environment Support**: Work with different Contentful environments (master, staging, etc.)

## Integration Points

### Existing Code Changes Required
- **File**: `backend/services/contentful.py`
  - Replace MockContentfulService with ContentfulClient
  - Implement real `get_article()` method using CDA/CMA
  - Implement real `write_activation_log()` creating Contentful entries
  - Add `create_activation_log_content_type()` setup method

- **File**: `backend/main.py`  
  - Update error handling for real Contentful failures
  - Add configuration validation on startup
  - Implement retry logic for API timeouts

### New Dependencies
```python
# backend/requirements.txt additions
contentful-management>=3.0.0
contentful>=1.13.0
```

### Configuration Updates
```bash
# .env.template additions
CONTENTFUL_SPACE_ID=your_space_id_here
CONTENTFUL_MANAGEMENT_TOKEN=your_management_token_here
CONTENTFUL_DELIVERY_TOKEN=your_delivery_token_here
CONTENTFUL_ENVIRONMENT=master
```

## Dependencies

- **Contentful Account**: Active Contentful account with space access
- **API Tokens**: Management token with content creation permissions
- **Content Model**: Article content type must exist in target space
- **Network Access**: Outbound HTTPS to `api.contentful.com` and `cdn.contentful.com`

## Risk Assessment

### High Risk
- **Token Security**: Management tokens grant full space access - secure storage required
- **Rate Limiting**: Contentful enforces strict rate limits - could impact activation performance
- **Content Model Dependency**: Changes to Contentful content models could break integration

### Medium Risk  
- **Network Reliability**: API failures could impact activation workflow
- **Field Mapping**: Different field configurations across Contentful spaces
- **Environment Consistency**: Differences between development and production spaces

### Mitigation Strategies
- **Graceful Degradation**: Continue with JSONL logging when Contentful unavailable  
- **Configuration Validation**: Startup checks for required tokens and space access
- **Field Validation**: Robust mapping with clear error messages for missing fields
- **Rate Limit Handling**: Exponential backoff and request queuing

## Expected Deliverable

A fully functional ContentfulService that:
1. Retrieves real articles from Contentful spaces
2. Creates ActivationLog entries as Contentful entries
3. Handles authentication, rate limiting, and error scenarios
4. Maintains backward compatibility with existing API contracts
5. Provides clear configuration and setup documentation

## Out of Scope (Future Iterations)

- Contentful webhook integration for automatic activations
- Multi-space support within single deployment
- Advanced content model synchronization
- Contentful extension/app SDK integration beyond basic API calls