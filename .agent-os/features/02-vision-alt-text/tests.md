# Test Specifications: Vision Alt Text Generation

## Overview
Comprehensive testing strategy for vision-powered alt text generation, ensuring quality, performance, and accessibility compliance.

## Test Coverage Requirements
- **Unit Tests**: 90% coverage for vision processing components
- **Integration Tests**: 100% coverage for vision service workflows
- **End-to-End Tests**: Complete alt text generation pipeline validation
- **Performance Tests**: Response time and throughput requirements
- **Quality Tests**: Accessibility and brand compliance validation

## Unit Tests

### Vision Service Provider Tests

#### Test Suite: OpenAI Vision Provider
```python
class TestOpenAIVisionProvider:
    def test_vision_api_integration(self):
        """Test successful gpt-4o vision API call"""
        provider = OpenAIVisionProvider()
        image_data = load_test_image("sample_marketing_dashboard.jpg")
        context = "Marketing automation dashboard screenshot"
        
        result = provider.generate_alt_text(image_data, context)
        
        assert result.alt_text is not None
        assert len(result.alt_text) >= 50
        assert len(result.alt_text) <= 150
        assert result.confidence_score > 0.7
        assert "dashboard" in result.alt_text.lower()
    
    def test_vision_api_error_handling(self):
        """Test graceful handling of OpenAI API errors"""
        provider = OpenAIVisionProvider(api_key="invalid_key")
        image_data = load_test_image("sample_image.jpg")
        
        result = provider.generate_alt_text(image_data, "test context")
        
        assert result.error is not None
        assert result.fallback is True
        assert result.alt_text is not None  # Should provide fallback text
        
    def test_image_format_validation(self):
        """Test handling of different image formats"""
        provider = OpenAIVisionProvider()
        
        # Test JPEG
        jpeg_data = load_test_image("test.jpg")
        result_jpeg = provider.generate_alt_text(jpeg_data, "context")
        assert result_jpeg.alt_text is not None
        
        # Test PNG
        png_data = load_test_image("test.png")
        result_png = provider.generate_alt_text(png_data, "context") 
        assert result_png.alt_text is not None
        
        # Test WebP
        webp_data = load_test_image("test.webp")
        result_webp = provider.generate_alt_text(webp_data, "context")
        assert result_webp.alt_text is not None
    
    def test_context_integration(self):
        """Test context-aware alt text generation"""
        provider = OpenAIVisionProvider()
        image_data = load_test_image("generic_chart.jpg")
        
        # Test marketing context
        marketing_result = provider.generate_alt_text(
            image_data, 
            "Article about marketing ROI and conversion rates"
        )
        assert any(word in marketing_result.alt_text.lower() 
                  for word in ['marketing', 'conversion', 'roi'])
        
        # Test technical context  
        tech_result = provider.generate_alt_text(
            image_data,
            "Technical documentation about API performance metrics"
        )
        assert any(word in tech_result.alt_text.lower()
                  for word in ['api', 'performance', 'metrics'])
```

#### Test Suite: Qwen Vision Provider
```python
class TestQwenVisionProvider:
    def test_local_model_integration(self):
        """Test Qwen 2.5VL 7b local model integration"""
        provider = QwenVisionProvider()
        image_data = load_test_image("sample_infographic.jpg")
        context = "Marketing infographic about email automation"
        
        result = provider.generate_alt_text(image_data, context)
        
        assert result.alt_text is not None
        assert result.provider == "qwen"
        assert result.processing_time_ms > 0
        assert "infographic" in result.alt_text.lower() or "chart" in result.alt_text.lower()
    
    def test_ollama_connection_failure(self):
        """Test handling of Ollama service unavailability"""
        provider = QwenVisionProvider(base_url="http://localhost:99999")  # Invalid port
        image_data = load_test_image("test.jpg")
        
        result = provider.generate_alt_text(image_data, "test")
        
        assert result.error is not None
        assert "connection" in result.error.lower()
        assert result.fallback is True
    
    def test_model_response_parsing(self):
        """Test parsing of Qwen model response format"""
        provider = QwenVisionProvider()
        
        # Mock Ollama response format
        mock_response = {
            "response": "Alt text: A detailed marketing dashboard showing conversion metrics and ROI data."
        }
        
        parsed_text = provider._parse_model_response(mock_response)
        
        assert parsed_text == "A detailed marketing dashboard showing conversion metrics and ROI data."
        assert not parsed_text.startswith("Alt text:")
```

### Image Processing Tests

#### Test Suite: Image Upload Validation
```python
class TestImageUploadValidation:
    def test_valid_image_formats(self):
        """Test acceptance of valid image formats"""
        validator = ImageValidator()
        
        # Test JPEG
        assert validator.validate_format("test.jpg") is True
        assert validator.validate_format("test.jpeg") is True
        
        # Test PNG
        assert validator.validate_format("test.png") is True
        
        # Test WebP
        assert validator.validate_format("test.webp") is True
    
    def test_invalid_image_formats(self):
        """Test rejection of invalid formats"""
        validator = ImageValidator()
        
        assert validator.validate_format("test.gif") is False
        assert validator.validate_format("test.bmp") is False
        assert validator.validate_format("test.svg") is False
        assert validator.validate_format("document.pdf") is False
    
    def test_file_size_validation(self):
        """Test file size limits"""
        validator = ImageValidator(max_size_mb=10)
        
        # Create test files of different sizes
        small_file = create_test_image(size_mb=1)
        large_file = create_test_image(size_mb=15)
        
        assert validator.validate_size(small_file) is True
        assert validator.validate_size(large_file) is False
    
    def test_malicious_file_detection(self):
        """Test detection of malicious files masquerading as images"""
        validator = ImageValidator()
        
        malicious_file = create_fake_image_with_script()
        
        assert validator.validate_security(malicious_file) is False
```

### Alt Text Quality Tests

#### Test Suite: Quality Validation
```python
class TestAltTextQuality:
    def test_length_optimization(self):
        """Test alt text length requirements"""
        validator = AltTextQualityValidator()
        
        # Optimal length (125-150 chars)
        optimal_text = "A marketing dashboard showing conversion rates and ROI metrics with clear data visualization and performance indicators"
        assert validator.validate_length(optimal_text).score >= 0.9
        
        # Too short
        short_text = "Dashboard"
        assert validator.validate_length(short_text).score < 0.5
        
        # Too long  
        long_text = "A" * 200
        assert validator.validate_length(long_text).score < 0.7
    
    def test_accessibility_compliance(self):
        """Test WCAG 2.1 compliance validation"""
        validator = AltTextQualityValidator()
        
        # Good accessibility
        good_text = "Marketing ROI dashboard displaying 45% conversion improvement and $2.3M revenue growth"
        compliance = validator.validate_accessibility(good_text)
        assert compliance.wcag_compliant is True
        
        # Poor accessibility (generic description)
        poor_text = "Image of stuff"
        compliance = validator.validate_accessibility(poor_text)
        assert compliance.wcag_compliant is False
        
        # Decorative image handling
        decorative_text = ""
        compliance = validator.validate_accessibility(decorative_text, is_decorative=True)
        assert compliance.wcag_compliant is True
    
    def test_keyword_integration(self):
        """Test integration of relevant keywords from context"""
        validator = AltTextQualityValidator()
        context_keywords = ["marketing automation", "conversion rate", "ROI"]
        
        alt_text = "Dashboard showing marketing automation performance with conversion rate metrics and ROI analysis"
        
        keyword_score = validator.validate_keyword_relevance(alt_text, context_keywords)
        assert keyword_score.score > 0.8
        assert keyword_score.keywords_found >= 2
```

## Integration Tests

### Vision Service Integration Tests

#### Test Suite: End-to-End Vision Pipeline
```python
class TestVisionPipelineIntegration:
    def test_complete_alt_text_generation_flow(self):
        """Test complete pipeline from image upload to alt text generation"""
        # Setup
        vision_service = VisionService()
        test_image = load_test_image("marketing_campaign_results.jpg")
        article_context = {
            "title": "Q4 Marketing Campaign Performance Review",
            "summary": "Analysis of email marketing campaign results and ROI",
            "keywords": ["email marketing", "campaign performance", "ROI"]
        }
        
        # Execute
        result = vision_service.generate_alt_text_with_context(
            image_data=test_image,
            context=article_context
        )
        
        # Verify
        assert result.success is True
        assert result.alt_text is not None
        assert len(result.alt_text) >= 50
        assert len(result.alt_text) <= 150
        assert result.confidence_score > 0.7
        assert any(keyword in result.alt_text.lower() for keyword in article_context["keywords"])
    
    def test_multiple_images_batch_processing(self):
        """Test processing multiple images in single article"""
        vision_service = VisionService()
        images = [
            load_test_image("dashboard_overview.jpg"),
            load_test_image("conversion_funnel.jpg"),
            load_test_image("roi_chart.jpg")
        ]
        
        results = vision_service.process_multiple_images(images, "Marketing performance analysis")
        
        assert len(results) == 3
        assert all(result.success for result in results)
        assert all(result.alt_text for result in results)
        assert all(len(result.alt_text) <= 150 for result in results)
    
    def test_provider_fallback_mechanism(self):
        """Test fallback from OpenAI to local model when API fails"""
        # Mock OpenAI failure
        with patch('openai.Client.chat.completions.create', side_effect=Exception("API Error")):
            vision_service = VisionService(primary_provider="openai", fallback_provider="qwen")
            image_data = load_test_image("test_chart.jpg")
            
            result = vision_service.generate_alt_text(image_data, "test context")
            
            assert result.success is True  # Should succeed via fallback
            assert result.provider == "qwen"  # Should use fallback provider
            assert result.fallback_used is True
```

### FastAPI Endpoint Integration Tests

#### Test Suite: Alt Text API Endpoints
```python
class TestAltTextEndpoints:
    def test_image_upload_endpoint(self):
        """Test /upload-image endpoint"""
        client = TestClient(app)
        
        # Create test image file
        test_image = create_test_image_file("test.jpg", format="JPEG")
        
        response = client.post(
            "/upload-image",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "image_id" in data
        assert "secure_url" in data
        assert data["format"] == "JPEG"
    
    def test_generate_alt_text_endpoint(self):
        """Test /generate-alt-text endpoint"""
        client = TestClient(app)
        
        payload = {
            "image_url": "https://example.com/test-image.jpg",
            "article_context": {
                "title": "Marketing Automation Best Practices",
                "summary": "Guide to effective email marketing campaigns",
                "keywords": ["email marketing", "automation", "conversion"]
            }
        }
        
        response = client.post("/generate-alt-text", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "alt_text" in data
        assert "confidence_score" in data
        assert "processing_time_ms" in data
        assert data["confidence_score"] > 0.0
    
    def test_enhanced_activation_endpoint_with_vision(self):
        """Test /activate endpoint with automatic alt text generation"""
        client = TestClient(app)
        
        # Mock Contentful article with images but no alt text
        article_with_images = {
            "sys": {"id": "test-entry-456"},
            "fields": {
                "title": "Email Marketing ROI Analysis",
                "body": "Comprehensive analysis of email campaign performance...",
                "campaignTags": ["email-marketing", "roi", "analytics"],
                "hasImages": True,
                "altText": None,  # Missing alt text - should be generated
                "imageUrls": ["https://example.com/email-dashboard.jpg"],
                "ctaText": "Download Report",
                "ctaUrl": "https://example.com/download"
            }
        }
        
        with patch("main.contentful_service.get_article", return_value=article_with_images):
            response = client.post("/activate", json={
                "entry_id": "test-entry-456",
                "marketo_list_id": "ML_TEST_001",
                "enrichment_enabled": True
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "vision_processing" in data
        assert data["vision_processing"]["alt_texts_generated"] > 0
```

## Performance Tests

### Response Time Tests

#### Test Suite: Performance Benchmarks
```python
class TestVisionPerformanceRequirements:
    def test_openai_response_time_requirement(self):
        """Test OpenAI vision response time <10 seconds"""
        provider = OpenAIVisionProvider()
        image_data = load_test_image("standard_dashboard.jpg")
        
        start_time = time.time()
        result = provider.generate_alt_text(image_data, "marketing dashboard")
        processing_time = time.time() - start_time
        
        assert processing_time < 10.0  # Must be under 10 seconds
        assert result.processing_time_ms == pytest.approx(processing_time * 1000, rel=0.1)
    
    def test_qwen_response_time_requirement(self):
        """Test Qwen local model response time <15 seconds"""
        provider = QwenVisionProvider()
        image_data = load_test_image("complex_infographic.jpg")
        
        start_time = time.time()
        result = provider.generate_alt_text(image_data, "marketing infographic")
        processing_time = time.time() - start_time
        
        assert processing_time < 15.0  # Must be under 15 seconds
        assert result.processing_time_ms > 0
    
    def test_concurrent_processing_capacity(self):
        """Test concurrent image processing capacity"""
        import asyncio
        import aiohttp
        
        async def process_image(session, image_data):
            async with session.post("/generate-alt-text", 
                                   json={"image_data": image_data, "context": "test"}) as response:
                return await response.json()
        
        async def test_concurrent():
            images = [load_test_image(f"test_{i}.jpg") for i in range(10)]
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                results = await asyncio.gather(*[process_image(session, img) for img in images])
                total_time = time.time() - start_time
            
            # Should handle 10 concurrent requests in reasonable time
            assert total_time < 30.0  # Concurrent processing efficiency
            assert len(results) == 10
            assert all(result.get("alt_text") for result in results)
        
        asyncio.run(test_concurrent())
```

### Load Testing

#### Test Suite: System Load Validation
```python
class TestVisionLoadCapacity:
    def test_sustained_load_processing(self):
        """Test processing 50+ images per hour capacity"""
        vision_service = VisionService()
        test_images = [load_test_image(f"load_test_{i}.jpg") for i in range(60)]
        
        start_time = time.time()
        successful_processes = 0
        
        for image in test_images:
            try:
                result = vision_service.generate_alt_text(image, "load test context")
                if result.success:
                    successful_processes += 1
            except Exception as e:
                print(f"Load test error: {e}")
        
        total_time = time.time() - start_time
        images_per_hour = (successful_processes / total_time) * 3600
        
        assert images_per_hour >= 50  # Minimum throughput requirement
        assert successful_processes >= 55  # >90% success rate under load
    
    def test_memory_usage_stability(self):
        """Test memory stability during extended processing"""
        import psutil
        import gc
        
        vision_service = VisionService()
        initial_memory = psutil.Process().memory_info().rss
        
        # Process 100 images to test for memory leaks
        for i in range(100):
            image_data = create_test_image(size_kb=500)  # 500KB test images
            result = vision_service.generate_alt_text(image_data, f"test context {i}")
            
            # Force garbage collection periodically
            if i % 10 == 0:
                gc.collect()
        
        final_memory = psutil.Process().memory_info().rss
        memory_increase = (final_memory - initial_memory) / (1024 * 1024)  # MB
        
        # Memory increase should be minimal (< 50MB for 100 images)
        assert memory_increase < 50, f"Memory leak detected: {memory_increase:.2f}MB increase"
```

## Quality Assurance Tests

### Brand Voice Compliance Tests

#### Test Suite: Brand Consistency Validation
```python
class TestBrandVoiceCompliance:
    def test_professional_tone_scoring(self):
        """Test brand voice professionalism scoring"""
        brand_analyzer = BrandVoiceAnalyzer()
        
        # Professional alt text
        professional_text = "Marketing automation dashboard displaying conversion metrics and ROI analysis for enterprise campaigns"
        score = brand_analyzer.analyze_professionalism(professional_text)
        assert score.score > 0.8
        
        # Unprofessional alt text
        unprofessional_text = "Awesome dashboard with cool stuff and amazing results!!!"
        score = brand_analyzer.analyze_professionalism(unprofessional_text)
        assert score.score < 0.5
    
    def test_accessibility_language_validation(self):
        """Test dual-audience accessibility in language"""
        brand_analyzer = BrandVoiceAnalyzer()
        
        # Technical but accessible
        accessible_text = "Content management system interface showing article publishing workflow and approval status"
        accessibility = brand_analyzer.analyze_accessibility(accessible_text)
        assert accessibility.technical_score > 0.7
        assert accessibility.readability_score > 0.7
        
        # Too technical
        technical_text = "CMS DOM interface depicting CRUD operations via RESTful API endpoints with JWT authentication tokens"
        accessibility = brand_analyzer.analyze_accessibility(technical_text)
        assert accessibility.readability_score < 0.5
    
    def test_action_oriented_language(self):
        """Test action-oriented language requirements"""
        brand_analyzer = BrandVoiceAnalyzer()
        
        # Action-oriented
        action_text = "Marketing dashboard enabling teams to track conversion rates and optimize campaign performance"
        action_score = brand_analyzer.analyze_action_orientation(action_text)
        assert action_score.score > 0.7
        
        # Passive language
        passive_text = "Marketing dashboard that shows various metrics and data points for viewing"
        action_score = brand_analyzer.analyze_action_orientation(passive_text)
        assert action_score.score < 0.5
```

### Accessibility Compliance Tests

#### Test Suite: WCAG 2.1 AA Compliance
```python
class TestAccessibilityCompliance:
    def test_wcag_alt_text_requirements(self):
        """Test WCAG 2.1 AA alt text requirements"""
        wcag_validator = WCAGValidator()
        
        # Informative image
        informative_text = "Bar chart showing 45% increase in email open rates over 6-month period"
        result = wcag_validator.validate_informative_image(informative_text)
        assert result.compliant is True
        assert result.guideline == "1.1.1"  # Non-text Content
        
        # Complex image requiring long description
        complex_text = "Detailed marketing funnel diagram - see full description below chart"
        result = wcag_validator.validate_complex_image(complex_text)
        assert result.requires_long_description is True
        
        # Decorative image (empty alt)
        decorative_result = wcag_validator.validate_decorative_image("")
        assert decorative_result.compliant is True
    
    def test_context_dependency_validation(self):
        """Test that alt text doesn't rely on surrounding context"""
        wcag_validator = WCAGValidator()
        
        # Context-dependent (bad)
        context_dependent = "As shown in the image above"
        result = wcag_validator.validate_context_independence(context_dependent)
        assert result.compliant is False
        
        # Self-contained (good)
        self_contained = "Marketing ROI dashboard displaying quarterly performance metrics"
        result = wcag_validator.validate_context_independence(self_contained)
        assert result.compliant is True
```

## Test Data Management

### Test Image Library
```python
class TestImageLibrary:
    """Centralized test image management"""
    
    @staticmethod
    def load_marketing_dashboard() -> bytes:
        """Load standard marketing dashboard test image"""
        return Path("test_data/images/marketing_dashboard.jpg").read_bytes()
    
    @staticmethod 
    def load_email_campaign_chart() -> bytes:
        """Load email campaign performance chart"""
        return Path("test_data/images/email_campaign_chart.png").read_bytes()
    
    @staticmethod
    def load_roi_infographic() -> bytes:
        """Load ROI analysis infographic"""
        return Path("test_data/images/roi_infographic.webp").read_bytes()
    
    @staticmethod
    def create_test_image(width: int = 800, height: int = 600, format: str = "JPEG") -> bytes:
        """Generate synthetic test image with specified dimensions"""
        from PIL import Image, ImageDraw
        import io
        
        image = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), "Test Marketing Dashboard", fill="black")
        
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return buffer.getvalue()
```

### Test Context Library  
```python
class TestContextLibrary:
    """Standard test contexts for consistent testing"""
    
    MARKETING_CONTEXTS = [
        {
            "title": "Q4 Email Marketing Performance Review",
            "summary": "Analysis of email campaign metrics and ROI",
            "keywords": ["email marketing", "campaign performance", "ROI"]
        },
        {
            "title": "Marketing Automation Platform Comparison", 
            "summary": "Evaluation of leading marketing automation tools",
            "keywords": ["marketing automation", "platform comparison", "features"]
        },
        {
            "title": "Content Marketing Strategy Guide",
            "summary": "Best practices for content creation and distribution",
            "keywords": ["content marketing", "strategy", "distribution"]
        }
    ]
    
    @classmethod
    def get_context(cls, context_type: str) -> dict:
        """Get standard test context by type"""
        contexts = {
            "email_marketing": cls.MARKETING_CONTEXTS[0],
            "automation": cls.MARKETING_CONTEXTS[1], 
            "content_strategy": cls.MARKETING_CONTEXTS[2]
        }
        return contexts.get(context_type, cls.MARKETING_CONTEXTS[0])
```

## Test Execution Strategy

### Continuous Integration Tests
- **Fast Tests**: Unit tests and basic integration (<30 seconds)
- **Standard Tests**: Full integration and API tests (<5 minutes)
- **Extended Tests**: Performance and load tests (<30 minutes)

### Pre-Deployment Validation
- **Quality Gate**: All unit and integration tests must pass
- **Performance Gate**: Response time requirements must be met
- **Security Gate**: No security vulnerabilities detected
- **Accessibility Gate**: WCAG 2.1 AA compliance verified

### Production Monitoring Tests
- **Health Checks**: Vision service availability and response time
- **Quality Monitoring**: Alt text quality scoring and human feedback
- **Performance Monitoring**: Response time and throughput tracking
- **Error Monitoring**: Vision API error rates and fallback usage

---

*Test Specifications v1.0 - Vision Alt Text Generation Feature*  
*Generated 2025-01-09 - Designed for comprehensive validation and quality assurance*