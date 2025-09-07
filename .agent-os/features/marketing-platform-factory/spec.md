# Marketing Platform Factory Technical Specification

This is the technical specification for the multi-platform marketing automation integration system enabling flexible destination routing for activated content in the AI Content Activation Engine.

> Created: 2025-09-06
> Version: 1.0.0
> Status: Implemented ✅
> Reference: @.agent-os/product/decisions.md ADR-004

## Technical Requirements

### Core Functionality
- **Multi-Platform Support**: Support Marketo, HubSpot, and mock services with unified interface
- **Dynamic Platform Selection**: Environment-based platform routing without code changes
- **Consistent API Contract**: Unified interface for content activation across all platforms
- **Graceful Degradation**: Mock service fallback for development and testing continuity

### Platform Integration Requirements
- **Marketo Integration**: REST API integration for campaign creation and content syndication
- **HubSpot Integration**: Marketing Hub API for content publishing and campaign management
- **Mock Service**: Realistic simulation for development and demonstration purposes
- **Future Platform Support**: Extensible architecture for additional platforms (Salesforce, Adobe)

### Data Processing Requirements
- **Content Transformation**: Map enriched content to platform-specific formats and requirements
- **Campaign Management**: Create and manage campaigns across different marketing platforms
- **Asset Handling**: Process and upload marketing assets (images, documents) to platforms
- **Metadata Synchronization**: Maintain consistent metadata and tracking across platforms

### Performance Requirements
- **Response Time**: <3 seconds for content publishing operations
- **Reliability**: 99.5% successful content delivery with proper error handling
- **Rate Limit Management**: Respect platform-specific API rate limits and quotas
- **Concurrent Operations**: Support parallel content activation to multiple platforms

## Approach

### Architecture Pattern
```python
# Marketing platform interface
class MarketingPlatform(ABC):
    @abstractmethod
    def create_campaign(self, campaign_data: Dict) -> CampaignResponse:
        """Create marketing campaign from activated content"""
        pass

    @abstractmethod
    def publish_content(self, content_data: Dict) -> PublishResponse:
        """Publish content to marketing platform"""
        pass

    @abstractmethod
    def upload_assets(self, assets: List[Asset]) -> AssetsResponse:
        """Upload marketing assets to platform"""
        pass

    @abstractmethod
    def get_campaign_status(self, campaign_id: str) -> StatusResponse:
        """Retrieve campaign status and metrics"""
        pass

# Factory pattern for platform selection
class MarketingPlatformFactory:
    @staticmethod
    def create_service() -> MarketingPlatform:
        platform = os.getenv("MARKETING_PLATFORM", "mock").lower()
        if platform == "marketo":
            return MarketoService()
        elif platform == "hubspot":
            return HubSpotService()
        return MockMarketingService()
```

### Implementation Strategy
1. **Platform Interface Definition**: Abstract base class defining marketing platform capabilities
2. **Platform-Specific Implementations**: Concrete implementations for each supported platform
3. **Content Mapping Layer**: Transform activated content to platform-specific formats
4. **Error Handling System**: Comprehensive error handling with platform-specific considerations
5. **Configuration Management**: Environment-based platform selection and credential management

### Integration Points
- **Content Activation Pipeline**: Receive activated content from AI enrichment process
- **ActivationLog Integration**: Record platform publishing results for audit trail
- **Asset Management**: Handle image and document assets from Contentful or other sources
- **Campaign Analytics**: Provide campaign performance data back to content creators

## External Dependencies

### Marketo Platform Dependencies
- **Marketo REST API**: Access to Marketo Marketing Automation REST API
- **Authentication**: OAuth 2.0 integration for secure API access
- **Campaign Management**: Programs, campaigns, and asset management capabilities
- **Rate Limiting**: Respect Marketo API rate limits (100 calls/20 seconds default)

### HubSpot Platform Dependencies
- **HubSpot Marketing Hub API**: Access to HubSpot's marketing automation APIs
- **Authentication**: API key or OAuth integration for secure access
- **Content Management**: Blog posts, landing pages, and email template management
- **Contact Management**: Integration with HubSpot CRM for audience targeting

### Mock Service Dependencies
- **Zero External Dependencies**: Mock service operates without external API calls
- **Realistic Simulation**: Simulate real platform behaviors and response patterns
- **Development Continuity**: Enable development and testing without platform costs
- **Error Simulation**: Configurable error scenarios for robustness testing

## Platform Specifications

### Marketo Service Implementation
```python
class MarketoService(MarketingPlatform):
    def __init__(self):
        self.client_id = os.getenv("MARKETO_CLIENT_ID")
        self.client_secret = os.getenv("MARKETO_CLIENT_SECRET")
        self.munchkin_id = os.getenv("MARKETO_MUNCHKIN_ID")
        self.base_url = f"https://{self.munchkin_id}.mktorest.com"
        self.access_token = None

    def create_campaign(self, campaign_data: Dict) -> CampaignResponse:
        """Create Marketo program and associated assets"""
        # Create program
        program_data = self._map_to_program(campaign_data)
        program_response = self._api_request("POST", "/rest/asset/v1/programs.json", program_data)

        # Create email template if needed
        if campaign_data.get("email_content"):
            email_data = self._map_to_email_template(campaign_data)
            email_response = self._api_request("POST", "/rest/asset/v1/emailTemplates.json", email_data)

        return CampaignResponse(
            success=True,
            campaign_id=program_response["result"][0]["id"],
            platform="marketo",
            details=program_response
        )
```

### HubSpot Service Implementation
```python
class HubSpotService(MarketingPlatform):
    def __init__(self):
        self.api_key = os.getenv("HUBSPOT_API_KEY")
        self.base_url = "https://api.hubapi.com"

    def create_campaign(self, campaign_data: Dict) -> CampaignResponse:
        """Create HubSpot campaign and content"""
        # Create blog post if content type is blog
        if campaign_data.get("content_type") == "blog":
            blog_data = self._map_to_blog_post(campaign_data)
            response = self._api_request("POST", "/content/api/v2/blog-posts", blog_data)

        # Create email campaign
        elif campaign_data.get("content_type") == "email":
            email_data = self._map_to_email_campaign(campaign_data)
            response = self._api_request("POST", "/marketing/v3/emails", email_data)

        return CampaignResponse(
            success=True,
            campaign_id=response["id"],
            platform="hubspot",
            details=response
        )
```

### Mock Service Implementation
```python
class MockMarketingService(MarketingPlatform):
    def create_campaign(self, campaign_data: Dict) -> CampaignResponse:
        """Mock campaign creation with realistic response"""
        campaign_id = f"mock_campaign_{int(time.time())}"

        # Simulate processing time
        time.sleep(0.5)

        return CampaignResponse(
            success=True,
            campaign_id=campaign_id,
            platform="mock",
            details={
                "message": "Mock campaign created successfully",
                "campaign_name": campaign_data.get("title", "Untitled Campaign"),
                "estimated_reach": random.randint(1000, 10000),
                "created_at": datetime.utcnow().isoformat()
            }
        )
```

## Data Transformation Layer

### Content Mapping System
```python
class ContentMapper:
    """Transform activated content to platform-specific formats"""

    def map_to_platform(self, activated_content: Dict, platform: str) -> Dict:
        """Map content to specific platform requirements"""
        if platform == "marketo":
            return self._map_to_marketo(activated_content)
        elif platform == "hubspot":
            return self._map_to_hubspot(activated_content)
        return self._map_to_generic(activated_content)

    def _map_to_marketo(self, content: Dict) -> Dict:
        """Transform content for Marketo program creation"""
        return {
            "name": content["title"],
            "description": content.get("meta_description", ""),
            "type": "program",
            "channel": self._determine_marketo_channel(content["campaign_tags"]),
            "costs": self._calculate_program_costs(content),
            "tags": self._map_tags_to_marketo(content["campaign_tags"])
        }

    def _map_to_hubspot(self, content: Dict) -> Dict:
        """Transform content for HubSpot campaign creation"""
        return {
            "name": content["title"],
            "content": content["body"],
            "meta_description": content.get("meta_description", ""),
            "topic_ids": self._map_tags_to_hubspot_topics(content["campaign_tags"]),
            "campaign_name": self._generate_campaign_name(content),
            "publish_date": datetime.utcnow().isoformat()
        }
```

### Campaign Response Models
```python
class CampaignResponse(BaseModel):
    success: bool
    campaign_id: str
    platform: str
    details: Dict
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PublishResponse(BaseModel):
    success: bool
    content_id: str
    platform: str
    public_url: Optional[str] = None
    error_message: Optional[str] = None

class AssetsResponse(BaseModel):
    success: bool
    asset_ids: List[str]
    platform: str
    asset_urls: List[str]
    error_message: Optional[str] = None
```

## Configuration Management

### Environment Variables
```bash
# Platform selection
MARKETING_PLATFORM=marketo|hubspot|mock

# Marketo configuration
MARKETO_CLIENT_ID=your_marketo_client_id
MARKETO_CLIENT_SECRET=your_marketo_client_secret
MARKETO_MUNCHKIN_ID=your_munchkin_id

# HubSpot configuration
HUBSPOT_API_KEY=your_hubspot_api_key
HUBSPOT_PORTAL_ID=your_portal_id

# Performance tuning
MARKETING_API_TIMEOUT=30
MARKETING_RETRY_ATTEMPTS=3
MARKETING_RATE_LIMIT_DELAY=1
```

### Platform Selection Logic
- **Production**: Configure specific platform based on client requirements
- **Development**: Use mock service for cost-free development and testing
- **Testing**: Mock service for deterministic testing outcomes
- **Multi-Platform**: Support for multiple platform activation simultaneously

## Error Handling Strategy

### Error Classification
```python
class MarketingPlatformError(Exception):
    """Base exception for marketing platform errors"""
    pass

class PlatformAuthenticationError(MarketingPlatformError):
    """Authentication failure with marketing platform"""
    pass

class ContentFormatError(MarketingPlatformError):
    """Content doesn't meet platform requirements"""
    pass

class PlatformRateLimitError(MarketingPlatformError):
    """Platform rate limit exceeded"""
    pass

class CampaignCreationError(MarketingPlatformError):
    """Campaign creation failed on platform"""
    pass
```

### Error Recovery Strategy
1. **Authentication Errors**: Attempt token refresh, then fail gracefully with clear message
2. **Rate Limiting**: Implement exponential backoff with intelligent retry logic
3. **Content Format Errors**: Provide detailed validation feedback for content correction
4. **Platform Outages**: Log error and continue with other platforms or mock fallback
5. **Partial Failures**: Complete successful operations and report specific failures

## Acceptance Criteria

### Functional Acceptance
- [ ] Successfully create campaigns on Marketo platform with proper authentication
- [ ] Successfully create campaigns on HubSpot platform with API integration
- [ ] Mock service provides realistic simulation for development and testing
- [ ] Content transformation works correctly for each platform's requirements
- [ ] Platform switching occurs seamlessly via environment configuration

### Performance Acceptance
- [ ] Campaign creation completes within 3-second response time requirement
- [ ] Rate limiting prevents API quota exhaustion for all platforms
- [ ] Concurrent platform operations execute efficiently without interference
- [ ] Error recovery maintains system responsiveness under platform failures
- [ ] Asset uploads complete successfully with proper error handling

### Quality Acceptance
- [ ] Content mapping preserves all important metadata and campaign information
- [ ] Error messages provide clear guidance for resolution and retry
- [ ] Platform-specific features work correctly (programs, topics, assets)
- [ ] Security requirements met for API key management and data transmission
- [ ] Mock service accuracy enables effective development and testing

### Integration Acceptance
- [ ] Marketing platform integration works seamlessly with content activation pipeline
- [ ] ActivationLog captures platform publishing results for comprehensive audit
- [ ] Asset handling processes images and documents correctly across platforms
- [ ] Campaign analytics provide useful feedback for content optimization
- [ ] Multi-platform activation distributes content correctly to multiple destinations

## Security Considerations

### API Security
- **Credential Management**: Secure storage and rotation of platform API credentials
- **Token Lifecycle**: Proper OAuth token management with automatic refresh
- **Access Permissions**: Use minimum required permissions for platform operations
- **Audit Logging**: Log all platform API access for security monitoring

### Data Security
- **Content Privacy**: Respect platform privacy settings and content restrictions
- **Data Transmission**: Use HTTPS for all platform API communications
- **Input Validation**: Validate all content before sending to platforms
- **Error Message Security**: Avoid exposing sensitive information in error responses

## Extensibility Framework

### Adding New Platforms
```python
# Template for new marketing platform integration
class NewPlatformService(MarketingPlatform):
    def __init__(self):
        self.api_key = os.getenv("NEWPLATFORM_API_KEY")
        self.client = NewPlatformClient(api_key=self.api_key)

    def create_campaign(self, campaign_data: Dict) -> CampaignResponse:
        # Platform-specific campaign creation
        pass

    def publish_content(self, content_data: Dict) -> PublishResponse:
        # Platform-specific content publishing
        pass

    # ... implement other required methods

# Factory update for new platform
def create_service() -> MarketingPlatform:
    platform = os.getenv("MARKETING_PLATFORM", "mock").lower()
    if platform == "newplatform":
        return NewPlatformService()
    # ... existing platform logic
```

### Configuration Extension Pattern
- **Environment Variables**: Standard pattern for platform-specific configuration
- **Authentication Methods**: Support for API keys, OAuth, and custom authentication
- **Content Mapping**: Extensible mapping system for platform-specific requirements
- **Performance Tuning**: Configurable timeouts, retries, and rate limiting per platform
