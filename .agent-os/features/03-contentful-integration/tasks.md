# Implementation Tasks: Live Contentful Integration

## Status: NOT IMPLEMENTED ❌
**Estimated Total Time:** 12-16 hours
**Priority:** CRITICAL (required for any real demonstration)

## Phase 1: Contentful Space Setup (3-4 hours)

### Task 1.1: Contentful Account & Space Creation
**Estimate**: 1 hour  
**Priority**: Critical
**Owner**: Manual setup required

**Steps:**
1. Create Contentful account (free tier sufficient for MVP)
2. Create new space for "Marketing Content Demo"  
3. Generate Content Management API tokens
4. Generate Content Delivery API tokens
5. Document space ID and tokens securely

**Acceptance Criteria:**
- [ ] Active Contentful space with unique space ID
- [ ] Content Management API token with read/write access
- [ ] Content Delivery API token for public content
- [ ] Preview API token for draft content
- [ ] Token security documentation

**Environment Setup:**
```bash
# Add to backend/.env
CONTENTFUL_SPACE_ID=your_actual_space_id
CONTENTFUL_ACCESS_TOKEN=your_delivery_token  
CONTENTFUL_PREVIEW_TOKEN=your_preview_token
CONTENTFUL_MANAGEMENT_TOKEN=your_management_token
```

### Task 1.2: Content Model Creation
**Estimate**: 2 hours
**Priority**: Critical

**Article Content Type Definition:**
```json
{
  "name": "Marketing Article",
  "displayField": "title", 
  "description": "Marketing content for AI activation",
  "fields": [
    {"id": "title", "name": "Title", "type": "Symbol", "required": true},
    {"id": "body", "name": "Body", "type": "RichText", "required": true},
    {"id": "summary", "name": "Summary", "type": "Text", "required": false},
    {"id": "campaignTags", "name": "Campaign Tags", "type": "Array", 
     "items": {"type": "Symbol", "validations": [{"in": ["thought-leadership", "marketer", "awareness", "case-study", "webinar", "ebook"]}]}},
    {"id": "hasImages", "name": "Has Images", "type": "Boolean", "required": false},
    {"id": "altText", "name": "Alt Text", "type": "Text", "required": false},
    {"id": "ctaText", "name": "CTA Text", "type": "Symbol", "required": false},
    {"id": "ctaUrl", "name": "CTA URL", "type": "Symbol", "required": false},
    {"id": "publishDate", "name": "Publish Date", "type": "Date", "required": false},
    {"id": "author", "name": "Author", "type": "Symbol", "required": false},
    {"id": "featuredImage", "name": "Featured Image", "type": "Link", "linkType": "Asset", "required": false}
  ]
}
```

**Implementation:**
- Use Contentful web interface for content model creation
- Configure field validations for campaign tags
- Set up field help text for content creators
- Test content model with sample entry

**Acceptance Criteria:**
- [ ] Marketing Article content type created
- [ ] All required fields configured with proper types
- [ ] Campaign tags validation with allowed values
- [ ] Test entry created successfully
- [ ] Content model matches Pydantic schema expectations

### Task 1.3: Sample Content Population  
**Estimate**: 1 hour
**Priority**: High

**Content Requirements:**
Create 5-10 sample articles with varied characteristics:

1. **AI Technology Blog Post**
   - Title: "The Future of AI in Marketing Automation"
   - Campaign Tags: ["thought-leadership", "marketer", "awareness"]
   - Has Images: true
   - CTA: "Download our AI Guide"

2. **Product Case Study**
   - Title: "How Enterprise Customer Increased ROI by 300%"  
   - Campaign Tags: ["case-study", "enterprise", "consideration"]
   - Has Images: true
   - CTA: "Schedule a Demo"

3. **Webinar Announcement**
   - Title: "Live Demo: Content Activation Platform"
   - Campaign Tags: ["webinar", "product-adoption", "decision"]
   - Has Images: false
   - CTA: "Register Now"

**Acceptance Criteria:**
- [ ] 10+ diverse marketing articles created
- [ ] Mixed content types (blog, case study, webinar, ebook)
- [ ] Various campaign tag combinations
- [ ] Some articles with images, some without
- [ ] Realistic content length (500+ words each)
- [ ] Valid CTAs with working URLs

## Phase 2: SDK Integration (4-6 hours)

### Task 2.1: Contentful SDK Installation
**Estimate**: 30 minutes
**Priority**: Critical

```bash
# Add to backend/requirements.txt
contentful>=1.12.0
python-dotenv>=0.19.0  # If not already present
```

**Implementation Steps:**
1. Update requirements.txt
2. Install in virtual environment
3. Test import functionality  
4. Add to Docker requirements if needed

**Acceptance Criteria:**
- [ ] Contentful SDK installed successfully
- [ ] No dependency conflicts
- [ ] Import test passes
- [ ] Docker compatibility verified

### Task 2.2: Real ContentfulService Implementation
**Estimate**: 3 hours
**Priority**: Critical

```python
# Replace mock implementation in backend/services/contentful.py
import contentful
from typing import Any, Optional

class ContentfulService:
    def __init__(self, 
                 space_id: str = None, 
                 access_token: str = None,
                 preview_token: str = None,
                 use_preview: bool = False):
        space_id = space_id or os.getenv('CONTENTFUL_SPACE_ID')
        access_token = access_token or os.getenv('CONTENTFUL_ACCESS_TOKEN')
        preview_token = preview_token or os.getenv('CONTENTFUL_PREVIEW_TOKEN')
        
        if not space_id or not access_token:
            raise ValueError("Contentful credentials not configured")
        
        # Use preview API for draft content, delivery API for published
        token = preview_token if use_preview else access_token
        api_url = 'preview.contentful.com' if use_preview else 'cdn.contentful.com'
        
        self.client = contentful.Client(space_id, token, api_url=api_url)
        self.space_id = space_id
    
    def get_article(self, entry_id: str) -> dict[str, Any]:
        """Retrieve article from Contentful CMS"""
        try:
            entry = self.client.entry(entry_id)
            return self._transform_entry(entry)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Article not found: {entry_id}")
    
    def _transform_entry(self, entry) -> dict[str, Any]:
        """Transform Contentful entry to expected format"""
        fields = {}
        
        # Extract and transform fields
        fields['title'] = getattr(entry, 'title', '')
        fields['body'] = self._rich_text_to_plain(getattr(entry, 'body', ''))
        fields['summary'] = getattr(entry, 'summary', None)
        fields['campaignTags'] = getattr(entry, 'campaign_tags', [])
        fields['hasImages'] = getattr(entry, 'has_images', False)
        fields['altText'] = getattr(entry, 'alt_text', None)  
        fields['ctaText'] = getattr(entry, 'cta_text', None)
        fields['ctaUrl'] = getattr(entry, 'cta_url', None)
        
        # Handle featured image asset
        featured_image = getattr(entry, 'featured_image', None)
        if featured_image:
            fields['hasImages'] = True
            if not fields['altText']:
                fields['altText'] = getattr(featured_image, 'description', '')
        
        return {
            'sys': {'id': entry.sys['id']},
            'fields': fields
        }
    
    def _rich_text_to_plain(self, rich_text) -> str:
        """Convert Contentful rich text to plain text"""
        if not rich_text:
            return ""
        
        # Handle both string and rich text object
        if isinstance(rich_text, str):
            return rich_text
        
        # Extract text content from rich text nodes
        def extract_text(node):
            if isinstance(node, dict):
                if node.get('nodeType') == 'text':
                    return node.get('value', '')
                elif 'content' in node:
                    return ''.join(extract_text(child) for child in node['content'])
            elif isinstance(node, list):
                return ''.join(extract_text(child) for child in node)
            return ''
        
        return extract_text(rich_text)
```

**Acceptance Criteria:**
- [ ] Real Contentful API connection established
- [ ] Entry retrieval working with sample content
- [ ] Field transformation matches Pydantic schema
- [ ] Rich text to plain text conversion
- [ ] Asset resolution for images
- [ ] Error handling for missing entries
- [ ] Preview/published content switching

### Task 2.3: Environment Configuration
**Estimate**: 1 hour  
**Priority**: High

**Configuration Management:**
```python
# Add environment validation to main.py
def validate_contentful_config():
    required_vars = [
        'CONTENTFUL_SPACE_ID',
        'CONTENTFUL_ACCESS_TOKEN'
    ]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"Warning: Missing Contentful config: {missing}")
        print("Falling back to mock service...")
        return False
    return True

# Initialize service based on configuration
if validate_contentful_config():
    contentful_service = ContentfulService()
else:
    # Keep mock as fallback
    contentful_service = MockContentfulService()
```

**Acceptance Criteria:**
- [ ] Environment variable validation
- [ ] Graceful fallback to mock service
- [ ] Clear error messages for missing config
- [ ] Documentation for setup process

## Phase 3: Testing & Validation (3-4 hours)

### Task 3.1: Integration Testing
**Estimate**: 2 hours
**Priority**: Critical

**New Test Cases:**
```python
# Add to backend/tests/test_contentful_integration.py
class TestContentfulIntegration:
    def test_real_contentful_connection(self):
        """Test connection to actual Contentful space"""
        
    def test_article_retrieval_with_real_data(self):
        """Test retrieving actual articles from Contentful"""
        
    def test_rich_text_conversion(self):
        """Test rich text to plain text conversion"""
        
    def test_asset_resolution(self):
        """Test image asset URL resolution"""
        
    def test_missing_entry_handling(self):
        """Test 404 handling for non-existent entries"""
        
    def test_field_mapping_validation(self):
        """Test all required fields map correctly"""
```

**Test Environment Setup:**
- Create test-specific Contentful entries
- Use environment variables for test credentials
- Mock external dependencies appropriately  
- Ensure tests clean up after themselves

**Acceptance Criteria:**
- [ ] All new integration tests pass
- [ ] Test coverage >90% for new code
- [ ] Tests run in CI/CD pipeline
- [ ] No test dependencies on production data

### Task 3.2: End-to-End Validation
**Estimate**: 2 hours
**Priority**: High

**Validation Scenarios:**
1. **Complete Activation Flow:**
   - Retrieve real article from Contentful
   - Validate against Pydantic schema
   - Process through AI enrichment
   - Send to marketing platform
   - Log activation results

2. **Error Handling:**
   - Invalid entry ID handling
   - Missing required fields graceful handling
   - Network timeout resilience
   - API rate limit respect

3. **Performance Testing:**
   - Response time under 2 seconds
   - Concurrent request handling
   - Memory usage optimization
   - Cache effectiveness

**Acceptance Criteria:**
- [ ] Full workflow runs with real Contentful data
- [ ] All error scenarios handled gracefully
- [ ] Performance targets met
- [ ] Memory leaks eliminated

## Phase 4: Documentation & Deployment (2-3 hours)

### Task 4.1: Setup Documentation
**Estimate**: 1 hour
**Priority**: Medium

**Documentation Requirements:**
```markdown
# Contentful Setup Guide

## Prerequisites
1. Contentful account (free tier sufficient)
2. Space creation and configuration
3. Content model setup
4. Sample content population

## Environment Configuration
- CONTENTFUL_SPACE_ID setup
- API token generation
- Security considerations

## Troubleshooting
- Common configuration errors
- Network connectivity issues
- API rate limit handling
```

**Acceptance Criteria:**
- [ ] Complete setup guide written
- [ ] Environment configuration documented
- [ ] Troubleshooting section comprehensive
- [ ] Screenshots for UI steps included

### Task 4.2: Deployment Preparation
**Estimate**: 2 hours
**Priority**: Medium

**Production Readiness:**
- Environment variable security audit
- API token rotation procedures
- Monitoring and alerting setup
- Backup and recovery planning

**Deployment Configuration:**
```yaml
# render.yaml updates for production deployment
services:
  - type: web
    name: contentful-bridge
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: CONTENTFUL_SPACE_ID
        sync: false  # Set manually for security
      - key: CONTENTFUL_ACCESS_TOKEN  
        sync: false  # Set manually for security
```

**Acceptance Criteria:**
- [ ] Production environment configured
- [ ] Security audit completed
- [ ] Monitoring setup verified
- [ ] Deployment tested successfully

## Risk Mitigation

### Technical Risks
- **Contentful API Changes**: Pin SDK version, test updates thoroughly
- **Network Connectivity**: Implement retry logic and timeouts
- **Rate Limiting**: Respect API limits, implement exponential backoff
- **Data Migration**: Backup mock data, provide fallback mechanisms

### Business Risks  
- **Demo Dependency**: Ensure stable demo environment separate from development
- **Content Quality**: Create high-quality sample content for demonstrations
- **Performance**: Load test with realistic content volumes
- **Security**: Audit token permissions, implement least-privilege access

## Success Criteria

### Technical Success
- [ ] Real Contentful space operational
- [ ] All sample articles retrievable via API
- [ ] Field mapping 100% accurate
- [ ] Performance under 2 seconds per request
- [ ] Error handling covers all edge cases

### Business Success
- [ ] Working demonstration capability
- [ ] Customer validation possible with real content
- [ ] Sales demo environment ready
- [ ] Production deployment feasible

### Quality Metrics
- [ ] Test coverage >95% for integration code
- [ ] Zero breaking changes to existing functionality
- [ ] Documentation completeness score >90%
- [ ] Security audit passes all checks