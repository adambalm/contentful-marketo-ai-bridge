# Contentful Live Integration Technical Specification

This is the technical specification for live Contentful CMS integration enabling real-time content activation workflows in the AI Content Activation Engine.

> Created: 2025-09-06
> Version: 1.0.0
> Status: Planned (Phase 2)
> Reference: @.agent-os/product/roadmap.md

## Technical Requirements

### Core Functionality
- **Real-Time Content Access**: Direct integration with Contentful Management API for live content retrieval
- **Content Model Synchronization**: Automatic sync with Contentful content types and field definitions
- **Authentication Management**: Secure API key and access token handling for Contentful spaces
- **Content Publishing Integration**: Seamless integration with Contentful's publishing workflow

### API Integration Requirements
- **Management API**: Full CRUD operations for content entries and assets
- **Delivery API**: Read-only access for published content retrieval
- **Preview API**: Access to draft content for staging workflows
- **Webhook Support**: Real-time notifications for content changes and publications

### Content Model Requirements
- **Article Content Type**: Title, body, summary, campaignTags, images, altText fields
- **Asset Management**: Image and media asset handling with CDN URLs
- **Entry Relationships**: Support for linked entries and references
- **Metadata Integration**: Created/updated timestamps, author information

### Performance Requirements
- **API Response Time**: <2 seconds for content retrieval operations
- **Sync Reliability**: 99.9% successful content synchronization
- **Rate Limit Management**: Respect Contentful API rate limits (7 req/sec Management API)
- **Caching Strategy**: Intelligent caching to minimize API calls and improve performance

## Approach

### Architecture Pattern
```python
# Contentful service interface
class ContentfulService:
    def __init__(self, space_id: str, access_token: str):
        self.client = contentful.Client(space_id, access_token)
        self.management_client = contentful_management.Client(access_token)

    async def get_article(self, entry_id: str) -> ContentfulArticle:
        """Retrieve article with all linked assets"""
        pass

    async def get_article_images(self, entry_id: str) -> List[ContentfulAsset]:
        """Get all images linked to an article"""
        pass

    async def update_article_alt_text(self, entry_id: str, alt_text: Dict[str, str]):
        """Update alt text for article images"""
        pass
```

### Implementation Strategy
1. **Contentful Client Setup**: Configure authenticated clients for Management and Delivery APIs
2. **Content Mapping**: Map Contentful entries to internal ArticleIn schema with validation
3. **Asset Processing**: Handle image assets with proper CDN URL resolution
4. **Webhook Integration**: Process real-time content change notifications
5. **Error Handling**: Robust error handling for API failures and network issues

### Integration Points
- **Content Validation**: Map Contentful entries to existing Pydantic ArticleIn schema
- **Vision Processing**: Trigger vision AI for images in live Contentful content
- **ActivationLog**: Record live content processing for audit and analytics
- **Marketing Platform**: Send activated content to configured marketing platforms

## External Dependencies

### Contentful Platform Dependencies
- **Contentful Space**: Active Contentful space with proper access permissions
- **API Tokens**: Management API token for full content operations
- **Content Models**: Article content type with required fields configured
- **CDN Access**: Reliable access to Contentful's asset CDN

### Python SDK Dependencies
- **contentful**: Official Contentful Python SDK for Delivery API
- **contentful-management**: Management API SDK for content operations
- **aiohttp**: Async HTTP client for improved performance
- **pydantic**: Data validation for Contentful content mapping

### Infrastructure Dependencies
- **Network Reliability**: Stable internet connection for API operations
- **SSL/TLS**: Secure connections for API authentication
- **DNS Resolution**: Reliable DNS for Contentful API endpoints
- **Rate Limiting**: Proper rate limit handling and backoff strategies

## Data Flow Architecture

### Content Retrieval Flow
1. **Entry Request**: Request specific article entry by ID
2. **Asset Resolution**: Resolve linked image assets with CDN URLs
3. **Schema Mapping**: Map Contentful fields to ArticleIn schema
4. **Validation**: Apply Pydantic validation and business rules
5. **Processing**: Execute AI enrichment and activation workflow

### Content Update Flow
1. **Processing Complete**: AI enrichment and activation completed
2. **Alt Text Update**: Update Contentful entry with generated alt text
3. **Metadata Update**: Add processing timestamps and activation status
4. **Webhook Notification**: Notify other systems of content changes
5. **Audit Logging**: Record all operations in ActivationLog

### Error Handling Flow
1. **API Error Detection**: Catch and classify Contentful API errors
2. **Retry Logic**: Implement exponential backoff for transient failures
3. **Fallback Strategy**: Graceful degradation to cached or mock content
4. **Error Logging**: Comprehensive error logging for debugging
5. **User Notification**: Clear error messages for content creators

## Security Considerations

### Authentication Security
- **API Token Management**: Secure storage and rotation of Contentful API tokens
- **Environment Variables**: Store sensitive credentials in environment variables
- **Token Scoping**: Use minimum required permissions for API access
- **Access Logging**: Log all API access for security monitoring

### Data Security
- **Content Privacy**: Respect Contentful's content privacy and access controls
- **Transmission Security**: Use HTTPS for all API communications
- **Data Validation**: Validate all incoming data from Contentful APIs
- **Error Message Security**: Avoid exposing sensitive information in error messages

## Acceptance Criteria

### Functional Acceptance
- [ ] Successfully authenticate with Contentful Management and Delivery APIs
- [ ] Retrieve live article content with all linked images and metadata
- [ ] Map Contentful entries to existing ArticleIn schema without data loss
- [ ] Process live content through existing AI enrichment pipeline
- [ ] Update Contentful entries with generated alt text and metadata

### Performance Acceptance
- [ ] Content retrieval completes within 2-second response time requirement
- [ ] Rate limit management prevents API quota exhaustion
- [ ] Caching strategy reduces redundant API calls by 70%
- [ ] Error handling maintains system stability under API failures
- [ ] Webhook processing handles real-time notifications reliably

### Quality Acceptance
- [ ] Data mapping preserves content integrity and metadata
- [ ] Generated alt text successfully updates in Contentful CMS
- [ ] Integration maintains existing test coverage standards (>95%)
- [ ] Error scenarios provide clear feedback to content creators
- [ ] Security requirements met for API token and data handling

### Integration Acceptance
- [ ] Live integration works seamlessly with existing activation workflow
- [ ] Vision processing operates on real Contentful images
- [ ] Brand voice analysis scores live content appropriately
- [ ] ActivationLog captures live content processing metadata
- [ ] Marketing platform integration receives live-activated content

## Phase Implementation Plan

### Phase 2.1: Basic Integration (Current Priority)
- Contentful space setup and API authentication
- Basic content retrieval and schema mapping
- Integration with existing activation pipeline
- Manual trigger for live content processing

### Phase 2.2: Enhanced Integration (Future)
- Webhook-driven automatic processing
- Real-time content synchronization
- Bulk content operations
- Advanced error handling and monitoring

### Phase 2.3: Production Optimization (Advanced)
- Intelligent caching and performance optimization
- Advanced rate limiting and quota management
- Multi-space support for enterprise deployments
- Comprehensive monitoring and analytics integration
