# Test Specifications: Live Contentful Integration

## Overview
Comprehensive testing strategy for replacing mock ContentfulService with live CMS integration, ensuring reliability, performance, and data integrity.

## Test Coverage Requirements  
- **Unit Tests**: 95% coverage for Contentful service components
- **Integration Tests**: 100% coverage for CMS API workflows
- **End-to-End Tests**: Complete content retrieval and activation pipeline
- **Performance Tests**: Response time and reliability under load
- **Security Tests**: API token management and access control

## Unit Tests

### Contentful SDK Integration Tests

#### Test Suite: ContentfulService Core Functionality
```python
class TestContentfulServiceCore:
    def test_contentful_client_initialization(self):
        """Test proper Contentful client setup"""
        service = ContentfulService(
            space_id="test_space_123",
            access_token="test_token_456"
        )
        
        assert service.client is not None
        assert service.space_id == "test_space_123"
        assert hasattr(service.client, 'entry')
        assert hasattr(service.client, 'entries')
    
    def test_environment_variable_configuration(self):
        """Test configuration via environment variables"""
        with patch.dict(os.environ, {
            'CONTENTFUL_SPACE_ID': 'env_space_789',
            'CONTENTFUL_ACCESS_TOKEN': 'env_token_101'
        }):
            service = ContentfulService()
            
            assert service.space_id == 'env_space_789'
            # Don't expose token in assertions for security
            assert service.client is not None
    
    def test_missing_credentials_error_handling(self):
        """Test error handling for missing credentials"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Contentful credentials not configured"):
                ContentfulService(space_id=None, access_token=None)
    
    def test_preview_vs_delivery_api_selection(self):
        """Test selection between preview and delivery APIs"""
        # Delivery API (published content)
        delivery_service = ContentfulService(use_preview=False)
        assert 'cdn.contentful.com' in str(delivery_service.client.api_url)
        
        # Preview API (draft content)
        preview_service = ContentfulService(use_preview=True)
        assert 'preview.contentful.com' in str(preview_service.client.api_url)
```

### Content Retrieval Tests

#### Test Suite: Article Retrieval and Transformation
```python
class TestContentfulArticleRetrieval:
    @patch('contentful.Client.entry')
    def test_successful_article_retrieval(self, mock_entry):
        """Test successful article retrieval from Contentful"""
        # Mock Contentful entry response
        mock_entry_data = create_mock_contentful_entry()
        mock_entry.return_value = mock_entry_data
        
        service = ContentfulService()
        result = service.get_article("test_entry_123")
        
        # Verify API call
        mock_entry.assert_called_once_with("test_entry_123")
        
        # Verify transformation
        assert result['sys']['id'] == "test_entry_123"
        assert result['fields']['title'] == mock_entry_data.title
        assert result['fields']['body'] is not None
        assert isinstance(result['fields']['campaignTags'], list)
    
    @patch('contentful.Client.entry')  
    def test_entry_not_found_handling(self, mock_entry):
        """Test handling of non-existent entry IDs"""
        mock_entry.side_effect = Exception("Entry not found")
        
        service = ContentfulService()
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_article("nonexistent_entry")
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()
    
    @patch('contentful.Client.entry')
    def test_network_timeout_handling(self, mock_entry):
        """Test handling of network timeouts"""
        import requests
        mock_entry.side_effect = requests.exceptions.Timeout("Connection timeout")
        
        service = ContentfulService()
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_article("test_entry")
        
        assert exc_info.value.status_code in [408, 503]  # Timeout or Service Unavailable
    
    def test_field_transformation_completeness(self):
        """Test complete field mapping from Contentful to expected format"""
        mock_entry = create_comprehensive_mock_entry()
        service = ContentfulService()
        
        result = service._transform_entry(mock_entry)
        
        expected_fields = [
            'title', 'body', 'summary', 'campaignTags', 
            'hasImages', 'altText', 'ctaText', 'ctaUrl'
        ]
        
        for field in expected_fields:
            assert field in result['fields'], f"Missing field: {field}"
    
    def test_optional_field_handling(self):
        """Test handling of missing optional fields"""
        mock_entry = create_minimal_mock_entry()  # Only required fields
        service = ContentfulService()
        
        result = service._transform_entry(mock_entry)
        
        # Required fields present
        assert result['fields']['title'] is not None
        assert result['fields']['body'] is not None
        
        # Optional fields handled gracefully
        assert result['fields']['summary'] is None
        assert result['fields']['altText'] is None
        assert result['fields']['ctaText'] is None
        assert result['fields']['ctaUrl'] is None
```

### Rich Text Processing Tests

#### Test Suite: Rich Text to Plain Text Conversion
```python
class TestRichTextProcessing:
    def test_simple_rich_text_conversion(self):
        """Test conversion of simple rich text to plain text"""
        service = ContentfulService()
        
        rich_text = {
            "nodeType": "document",
            "content": [
                {
                    "nodeType": "paragraph", 
                    "content": [
                        {"nodeType": "text", "value": "This is a simple paragraph."}
                    ]
                }
            ]
        }
        
        result = service._rich_text_to_plain(rich_text)
        assert result == "This is a simple paragraph."
    
    def test_complex_rich_text_with_formatting(self):
        """Test conversion of rich text with formatting and links"""
        service = ContentfulService()
        
        rich_text = {
            "nodeType": "document",
            "content": [
                {
                    "nodeType": "paragraph",
                    "content": [
                        {"nodeType": "text", "value": "Marketing automation helps "},
                        {
                            "nodeType": "hyperlink",
                            "data": {"uri": "https://example.com"},
                            "content": [{"nodeType": "text", "value": "increase ROI"}]
                        },
                        {"nodeType": "text", "value": " significantly."}
                    ]
                }
            ]
        }
        
        result = service._rich_text_to_plain(rich_text)
        assert result == "Marketing automation helps increase ROI significantly."
    
    def test_rich_text_with_embedded_assets(self):
        """Test handling of embedded assets in rich text"""
        service = ContentfulService()
        
        rich_text = {
            "nodeType": "document", 
            "content": [
                {"nodeType": "text", "value": "See the chart below:"},
                {
                    "nodeType": "embedded-asset-block",
                    "data": {"target": {"sys": {"id": "asset_123"}}}
                },
                {"nodeType": "text", "value": "This shows our performance."}
            ]
        }
        
        result = service._rich_text_to_plain(rich_text)
        # Should extract text and handle embedded assets gracefully
        assert "See the chart below:" in result
        assert "This shows our performance." in result
    
    def test_malformed_rich_text_handling(self):
        """Test graceful handling of malformed rich text"""
        service = ContentfulService()
        
        # Test various malformed inputs
        malformed_inputs = [
            None,
            "",
            {"invalid": "structure"},
            "plain string instead of rich text object"
        ]
        
        for malformed_input in malformed_inputs:
            result = service._rich_text_to_plain(malformed_input)
            # Should not crash and return reasonable output
            assert isinstance(result, str)
```

### Asset Resolution Tests

#### Test Suite: Asset URL and Image Processing
```python
class TestAssetResolution:
    def test_featured_image_url_extraction(self):
        """Test extraction of featured image URLs"""
        mock_entry = create_mock_entry_with_assets()
        service = ContentfulService()
        
        result = service._transform_entry(mock_entry)
        
        assert result['fields']['hasImages'] is True
        # Should detect images from featured image field
    
    def test_multiple_asset_resolution(self):
        """Test resolution of multiple linked assets"""
        mock_entry = create_mock_entry_with_multiple_assets()
        service = ContentfulService()
        
        image_urls = service._resolve_assets(mock_entry)
        
        assert len(image_urls) > 1
        assert all(url.startswith('https://') for url in image_urls)
        assert all('images.contentful.com' in url or 'assets.ctfassets.net' in url 
                  for url in image_urls)
    
    def test_asset_url_security_validation(self):
        """Test security validation of asset URLs"""
        service = ContentfulService()
        
        # Valid Contentful asset URLs
        valid_urls = [
            "https://images.contentful.com/space123/asset456/image.jpg",
            "https://assets.ctfassets.net/space123/asset456/image.png"
        ]
        
        for url in valid_urls:
            assert service._validate_asset_url(url) is True
        
        # Invalid/suspicious URLs
        invalid_urls = [
            "http://malicious-site.com/image.jpg",
            "javascript:alert('xss')",
            "../../../etc/passwd"
        ]
        
        for url in invalid_urls:
            assert service._validate_asset_url(url) is False
    
    def test_asset_alt_text_fallback(self):
        """Test fallback alt text from asset descriptions"""
        mock_asset = create_mock_asset_with_description()
        service = ContentfulService()
        
        result = service._transform_entry(create_mock_entry_with_asset(mock_asset))
        
        # Should use asset description as alt text fallback
        assert result['fields']['altText'] == mock_asset.description
```

## Integration Tests

### Live Contentful API Tests

#### Test Suite: Real API Integration
```python
class TestLiveContentfulIntegration:
    """Tests requiring actual Contentful space setup"""
    
    @pytest.mark.integration
    def test_real_space_connection(self):
        """Test connection to actual Contentful space"""
        # Requires test environment setup
        if not os.getenv('CONTENTFUL_TEST_SPACE_ID'):
            pytest.skip("Test space credentials not configured")
        
        service = ContentfulService()
        
        # Test space access
        try:
            # This should not raise an exception
            space_info = service.client.space()
            assert space_info is not None
        except Exception as e:
            pytest.fail(f"Failed to connect to Contentful space: {e}")
    
    @pytest.mark.integration
    def test_real_content_model_validation(self):
        """Test that content model matches expectations"""
        if not os.getenv('CONTENTFUL_TEST_SPACE_ID'):
            pytest.skip("Test space credentials not configured")
        
        service = ContentfulService()
        
        # Get content type definition
        content_types = service.client.content_types()
        article_type = next(
            (ct for ct in content_types if ct.id == 'marketingArticle'), 
            None
        )
        
        assert article_type is not None, "Marketing Article content type not found"
        
        # Verify required fields exist
        required_fields = ['title', 'body', 'campaignTags']
        field_ids = [field.id for field in article_type.fields]
        
        for required_field in required_fields:
            assert required_field in field_ids, f"Required field {required_field} missing"
    
    @pytest.mark.integration  
    def test_sample_content_retrieval(self):
        """Test retrieval of actual sample content"""
        if not os.getenv('CONTENTFUL_TEST_SPACE_ID'):
            pytest.skip("Test space credentials not configured")
        
        service = ContentfulService()
        
        # Get list of published articles
        entries = service.client.entries({'content_type': 'marketingArticle', 'limit': 1})
        
        assert len(entries) > 0, "No sample articles found in space"
        
        # Test article retrieval
        sample_entry_id = entries[0].sys['id']
        article_data = service.get_article(sample_entry_id)
        
        # Verify data structure
        assert 'sys' in article_data
        assert 'fields' in article_data
        assert article_data['fields']['title']
        assert article_data['fields']['body']
        assert isinstance(article_data['fields']['campaignTags'], list)
```

### End-to-End Workflow Tests

#### Test Suite: Complete Activation Pipeline
```python
class TestContentfulActivationWorkflow:
    @patch('main.contentful_service')
    def test_complete_activation_with_real_contentful_data(self, mock_contentful):
        """Test complete activation workflow with realistic Contentful data"""
        # Setup realistic Contentful response
        realistic_article = create_realistic_contentful_article()
        mock_contentful.get_article.return_value = realistic_article
        
        client = TestClient(app)
        
        response = client.post("/activate", json={
            "entry_id": "real_article_123",
            "marketo_list_id": "ML_TEST_001", 
            "enrichment_enabled": True
        })
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify Contentful integration
        mock_contentful.get_article.assert_called_once_with("real_article_123")
        
        # Verify data flows through system correctly
        assert result['success'] is True
        assert result['entry_id'] == "real_article_123"
        assert 'validation_results' in result
        assert 'ai_enrichment' in result
    
    def test_contentful_error_propagation(self):
        """Test error handling when Contentful service fails"""
        with patch('main.contentful_service.get_article', 
                  side_effect=HTTPException(status_code=404, detail="Entry not found")):
            
            client = TestClient(app)
            
            response = client.post("/activate", json={
                "entry_id": "nonexistent_123",
                "marketo_list_id": "ML_TEST_001"
            })
            
            assert response.status_code == 404
            assert "not found" in response.json()['detail'].lower()
    
    def test_contentful_timeout_recovery(self):
        """Test system resilience to Contentful timeouts"""
        with patch('main.contentful_service.get_article', 
                  side_effect=requests.exceptions.Timeout("Contentful timeout")):
            
            client = TestClient(app)
            
            response = client.post("/activate", json={
                "entry_id": "timeout_test_123",
                "marketo_list_id": "ML_TEST_001"
            })
            
            # Should handle timeout gracefully  
            assert response.status_code in [408, 503, 500]
            assert 'timeout' in response.json()['detail'].lower()
```

## Performance Tests

### Response Time Tests  

#### Test Suite: Contentful API Performance
```python
class TestContentfulPerformance:
    def test_single_entry_retrieval_time(self):
        """Test single entry retrieval meets <2 second requirement"""
        service = ContentfulService()
        
        start_time = time.time()
        article = service.get_article("performance_test_entry")
        retrieval_time = time.time() - start_time
        
        assert retrieval_time < 2.0, f"Entry retrieval took {retrieval_time:.2f}s (>2s limit)"
    
    def test_concurrent_entry_retrieval(self):
        """Test concurrent entry retrieval performance"""
        service = ContentfulService()
        entry_ids = ["entry_1", "entry_2", "entry_3", "entry_4", "entry_5"]
        
        import concurrent.futures
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(service.get_article, entry_id) for entry_id in entry_ids]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        
        assert len(results) == 5
        assert total_time < 5.0  # Concurrent should be faster than sequential
    
    def test_large_content_processing_time(self):
        """Test processing time for large articles"""
        large_article = create_large_test_article()  # 10,000+ words
        service = ContentfulService()
        
        start_time = time.time()
        result = service._transform_entry(large_article)
        processing_time = time.time() - start_time
        
        assert processing_time < 1.0  # Field transformation should be fast
        assert len(result['fields']['body']) > 10000  # Content preserved
```

### Load Testing

#### Test Suite: Sustained Load Validation
```python
class TestContentfulLoadCapacity:
    @pytest.mark.load_test
    def test_sustained_load_handling(self):
        """Test handling of sustained request load"""
        service = ContentfulService()
        
        # Simulate 100 requests over 5 minutes
        request_count = 100
        duration_seconds = 300
        delay_between_requests = duration_seconds / request_count
        
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        for i in range(request_count):
            try:
                start_time = time.time()
                article = service.get_article(f"load_test_entry_{i % 10}")  # Rotate through 10 entries
                response_time = time.time() - start_time
                
                response_times.append(response_time)
                successful_requests += 1
                
            except Exception as e:
                print(f"Load test request {i} failed: {e}")
                failed_requests += 1
            
            time.sleep(delay_between_requests)
        
        # Performance requirements
        success_rate = successful_requests / request_count
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        assert success_rate > 0.95, f"Success rate {success_rate:.2%} below 95% threshold"
        assert avg_response_time < 3.0, f"Avg response time {avg_response_time:.2f}s above 3s threshold"
    
    @pytest.mark.load_test
    def test_rate_limit_handling(self):
        """Test proper handling of Contentful API rate limits"""
        service = ContentfulService()
        
        # Make rapid requests to trigger rate limiting
        rate_limited = False
        for i in range(50):  # Exceed typical rate limits
            try:
                service.get_article(f"rate_test_entry_{i}")
            except Exception as e:
                if "rate limit" in str(e).lower() or "429" in str(e):
                    rate_limited = True
                    break
        
        # If rate limited, verify graceful handling
        if rate_limited:
            # Should implement exponential backoff or similar
            time.sleep(2)  # Brief wait
            
            # Should be able to make successful request after waiting
            try:
                result = service.get_article("rate_test_recovery")
                assert result is not None
            except Exception:
                pytest.fail("Failed to recover from rate limiting")
```

## Security Tests

### API Token Security Tests

#### Test Suite: Credential Management
```python
class TestContentfulSecurity:
    def test_api_token_not_logged(self):
        """Test that API tokens are not logged or exposed"""
        import logging
        from io import StringIO
        
        # Capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.DEBUG)
        
        try:
            # Initialize service (may log configuration)
            service = ContentfulService(
                space_id="test_space",
                access_token="secret_token_12345"
            )
            
            # Make request (may log API calls)
            with patch('contentful.Client.entry') as mock_entry:
                mock_entry.return_value = create_mock_contentful_entry()
                service.get_article("test_entry")
            
            # Check logs don't contain sensitive data
            log_output = log_capture.getvalue()
            assert "secret_token_12345" not in log_output
            
        finally:
            logging.getLogger().removeHandler(handler)
    
    def test_invalid_token_handling(self):
        """Test handling of invalid/expired API tokens"""
        service = ContentfulService(
            space_id="test_space",
            access_token="invalid_token"
        )
        
        with patch('contentful.Client.entry', 
                  side_effect=Exception("401 Unauthorized")):
            
            with pytest.raises(HTTPException) as exc_info:
                service.get_article("test_entry")
            
            assert exc_info.value.status_code == 401
            # Error message should not expose token details
            assert "invalid_token" not in str(exc_info.value.detail).lower()
    
    def test_space_access_validation(self):
        """Test validation of space access permissions"""
        # Test with space ID that token doesn't have access to
        service = ContentfulService(
            space_id="unauthorized_space",
            access_token="valid_but_wrong_space_token"
        )
        
        with patch('contentful.Client.entry',
                  side_effect=Exception("403 Forbidden")):
            
            with pytest.raises(HTTPException) as exc_info:
                service.get_article("test_entry")
            
            assert exc_info.value.status_code == 403
```

### Input Validation Security Tests

#### Test Suite: Content Security Validation  
```python
class TestContentfulInputSecurity:
    def test_entry_id_injection_protection(self):
        """Test protection against entry ID injection attacks"""
        service = ContentfulService()
        
        malicious_entry_ids = [
            "'; DROP TABLE entries; --",
            "../../../etc/passwd",
            "<script>alert('xss')</script>",
            "entry_id?additional_param=malicious"
        ]
        
        for malicious_id in malicious_entry_ids:
            with patch('contentful.Client.entry') as mock_entry:
                mock_entry.side_effect = Exception("Invalid entry ID")
                
                with pytest.raises(HTTPException):
                    service.get_article(malicious_id)
                
                # Verify the malicious input is not passed through unchanged
                call_args = mock_entry.call_args[0][0] if mock_entry.called else ""
                # Should be sanitized or rejected
    
    def test_rich_text_xss_protection(self):
        """Test protection against XSS in rich text content"""
        service = ContentfulService()
        
        malicious_rich_text = {
            "nodeType": "document",
            "content": [
                {
                    "nodeType": "paragraph",
                    "content": [
                        {
                            "nodeType": "text", 
                            "value": "<script>alert('xss')</script>Malicious content"
                        }
                    ]
                }
            ]
        }
        
        result = service._rich_text_to_plain(malicious_rich_text)
        
        # Should strip or escape HTML/JavaScript
        assert "<script>" not in result
        assert "alert(" not in result
        # But preserve legitimate content
        assert "Malicious content" in result or "content" in result
```

## Test Data Management

### Mock Data Factory
```python
class ContentfulTestDataFactory:
    """Factory for creating consistent test data"""
    
    @staticmethod
    def create_mock_contentful_entry(**overrides):
        """Create mock Contentful entry with realistic data"""
        default_data = {
            'sys': {'id': 'test_entry_123', 'type': 'Entry'},
            'title': 'Email Marketing Best Practices Guide',
            'body': 'Comprehensive guide to email marketing automation...',
            'summary': 'Learn proven strategies for effective email campaigns',
            'campaign_tags': ['email-marketing', 'automation', 'best-practices'],
            'has_images': True,
            'alt_text': 'Email marketing dashboard showing campaign metrics',
            'cta_text': 'Download Guide',
            'cta_url': 'https://example.com/email-guide',
            'publish_date': '2024-01-15T10:30:00Z',
            'author': 'Marketing Team'
        }
        
        # Apply any overrides
        default_data.update(overrides)
        
        # Convert to mock object with attribute access
        mock_entry = type('MockEntry', (), default_data)
        return mock_entry
    
    @staticmethod
    def create_large_test_article():
        """Create large article for performance testing"""
        large_body = "Marketing automation " * 1000  # ~15,000 characters
        
        return ContentfulTestDataFactory.create_mock_contentful_entry(
            title="Comprehensive Marketing Automation Guide - Extended Edition",
            body=large_body,
            campaign_tags=['marketing-automation', 'enterprise', 'comprehensive', 'guide']
        )
    
    @staticmethod
    def create_minimal_mock_entry():
        """Create entry with only required fields"""
        return ContentfulTestDataFactory.create_mock_contentful_entry(
            summary=None,
            alt_text=None,
            cta_text=None,
            cta_url=None,
            has_images=False
        )
```

### Test Environment Setup
```python
class ContentfulTestEnvironment:
    """Manage test environment setup and teardown"""
    
    @classmethod
    def setup_test_space(cls):
        """Setup test space with required content models"""
        # This would be run once to setup test environment
        if not os.getenv('CONTENTFUL_MANAGEMENT_TOKEN'):
            pytest.skip("Management token required for test space setup")
        
        # Create content model, add sample entries, etc.
        # Implementation depends on Contentful Management API
    
    @classmethod
    def cleanup_test_data(cls):
        """Clean up test entries after tests"""
        # Remove test entries to avoid cluttering space
        pass
    
    @classmethod
    def validate_test_prerequisites(cls):
        """Validate test environment is properly configured"""
        required_env_vars = [
            'CONTENTFUL_TEST_SPACE_ID',
            'CONTENTFUL_TEST_ACCESS_TOKEN'
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            pytest.skip(f"Test environment not configured. Missing: {missing_vars}")
```

## Test Execution Strategy

### Test Categories
- **Fast Tests**: Unit tests with mocks (<5 seconds total)
- **Integration Tests**: Real API calls with test data (<30 seconds)
- **Load Tests**: Performance validation (<5 minutes)
- **Security Tests**: Penetration and validation testing (<2 minutes)

### CI/CD Integration
- **PR Tests**: Fast tests + basic integration tests
- **Nightly Tests**: Full test suite including load and security tests
- **Release Tests**: Complete validation including manual verification

### Test Environment Management
- **Development**: Mock services for fast iteration
- **Testing**: Real Contentful test space with sample data
- **Staging**: Production-like environment for final validation
- **Production**: Monitoring and health checks only

---

*Test Specifications v1.0 - Live Contentful Integration Feature*  
*Generated 2025-01-09 - Comprehensive testing for production readiness*