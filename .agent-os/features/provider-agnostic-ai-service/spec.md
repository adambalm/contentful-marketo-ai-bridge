# Provider-Agnostic AI Service Technical Specification

This is the technical specification for the flexible AI provider integration system enabling vendor-independent AI capabilities in the AI Content Activation Engine.

> Created: 2025-09-06
> Version: 1.0.0
> Status: Implemented ✅
> Reference: @.agent-os/product/decisions.md ADR-001

## Technical Requirements

### Core Functionality
- **Multi-Provider Support**: Support OpenAI, local models (Ollama), and extensible to future providers
- **Runtime Provider Switching**: Environment-based provider selection without code changes
- **Unified Interface**: Consistent API across all providers for text and vision processing
- **Fallback Strategy**: Graceful degradation between providers based on availability and cost

### Provider Requirements
- **OpenAI Integration**: GPT models for text processing, gpt-4o for vision capabilities
- **Local Model Support**: Ollama integration for cost-effective development and privacy
- **Mock Provider**: Development and testing provider for continuous integration
- **Extension Framework**: Abstract interfaces enabling future provider additions

### Performance Requirements
- **Response Time**: <5 seconds for text processing, <10 seconds for vision processing
- **Reliability**: 99.5% success rate with proper error handling and retry logic
- **Cost Optimization**: Intelligent provider selection based on cost and capability requirements
- **Resource Management**: Efficient connection pooling and rate limiting

### Quality Requirements
- **Consistency**: Similar output quality across different providers for comparable models
- **Error Handling**: Comprehensive error classification and graceful degradation
- **Monitoring**: Detailed logging and metrics for provider performance analysis
- **Security**: Secure API key management and request/response handling

## Approach

### Architecture Pattern
```python
# Provider interface definition
class AIProvider(ABC):
    @abstractmethod
    def generate_content(self, prompt: str, context: Dict) -> str:
        """Generate content based on prompt and context"""
        pass
    
    @abstractmethod
    def generate_alt_text(self, image_url: str, context: str) -> str:
        """Generate alt text for images (vision-capable providers only)"""
        pass
    
    @abstractmethod
    def analyze_brand_voice(self, content: str) -> Dict[str, str]:
        """Analyze content for brand voice compliance"""
        pass

# Factory pattern for provider selection
class AIServiceFactory:
    @staticmethod
    def create_service() -> AIProvider:
        provider = os.getenv("AI_PROVIDER", "openai").lower()
        if provider == "local":
            return LocalModelProvider()
        elif provider == "mock":
            return MockAIProvider()
        return OpenAIProvider()
```

### Implementation Strategy
1. **Abstract Provider Interface**: Define common capabilities across all AI providers
2. **Provider Implementations**: Concrete implementations for OpenAI, local models, and mocks
3. **Factory Pattern**: Dynamic provider instantiation based on configuration
4. **Error Handling Layer**: Consistent error handling and provider fallback logic
5. **Configuration Management**: Environment-based provider selection and configuration

### Integration Points
- **Content Processing**: Integrate with content activation pipeline for text enrichment
- **Vision Processing**: Support vision capabilities through provider interface
- **Brand Voice Analysis**: Standardized brand voice scoring across providers
- **ActivationLog**: Record provider metadata and processing results for audit

## External Dependencies

### OpenAI Provider Dependencies
- **OpenAI Python SDK**: Latest OpenAI client library for API integration
- **API Key Management**: Secure credential handling for OpenAI API access
- **Model Configuration**: Support for different GPT models based on use case
- **Rate Limiting**: Respect OpenAI API rate limits and quota management

### Local Provider Dependencies
- **Ollama Integration**: Local model serving infrastructure
- **Model Management**: Local model installation and version management
- **Resource Allocation**: CPU/GPU resource management for local inference
- **Performance Optimization**: Efficient local model serving and caching

### Mock Provider Dependencies
- **Deterministic Responses**: Consistent mock responses for testing
- **Response Simulation**: Realistic response patterns and timing
- **Error Simulation**: Configurable error scenarios for testing robustness
- **Development Continuity**: Zero external dependencies for continuous integration

## Provider Specifications

### OpenAI Provider
```python
class OpenAIProvider(AIProvider):
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.text_model = os.getenv("OPENAI_TEXT_MODEL", "gpt-4o-mini")
        self.vision_model = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")
    
    def generate_content(self, prompt: str, context: Dict) -> str:
        # GPT-4o-mini for cost-effective text processing
        response = self.client.chat.completions.create(
            model=self.text_model,
            messages=[
                {"role": "system", "content": self._build_system_prompt(context)},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
```

### Local Model Provider
```python
class LocalModelProvider(AIProvider):
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.text_model = os.getenv("LOCAL_TEXT_MODEL", "llama2")
        self.vision_model = os.getenv("LOCAL_VISION_MODEL", "qwen2.5vl")
    
    def generate_content(self, prompt: str, context: Dict) -> str:
        # Ollama API integration for local models
        response = requests.post(f"{self.ollama_url}/api/generate", json={
            "model": self.text_model,
            "prompt": self._format_prompt(prompt, context),
            "stream": False
        })
        return response.json()["response"]
```

### Mock Provider
```python
class MockAIProvider(AIProvider):
    def generate_content(self, prompt: str, context: Dict) -> str:
        # Deterministic mock responses for testing
        if "meta description" in prompt.lower():
            return "Professional AI-powered content activation platform for marketing operations"
        elif "social media" in prompt.lower():
            return "Transform your marketing operations with AI-powered content activation #MarTech"
        return "Mock AI generated content for testing purposes"
```

## Configuration Management

### Environment Variables
```bash
# Provider selection
AI_PROVIDER=openai|local|mock

# OpenAI configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_TEXT_MODEL=gpt-4o-mini
OPENAI_VISION_MODEL=gpt-4o
OPENAI_ORGANIZATION=your_org_id

# Local model configuration  
OLLAMA_URL=http://localhost:11434
LOCAL_TEXT_MODEL=llama2
LOCAL_VISION_MODEL=qwen2.5vl

# Performance tuning
AI_TIMEOUT=30
AI_RETRY_ATTEMPTS=3
AI_RATE_LIMIT_RPM=60
```

### Provider Selection Logic
- **Production**: Default to OpenAI for reliability and quality
- **Development**: Local models for cost control and privacy
- **Testing**: Mock providers for deterministic testing
- **Fallback**: Automatic fallback to mock provider on provider failures

## Error Handling Strategy

### Error Classification
```python
class AIProviderError(Exception):
    """Base exception for AI provider errors"""
    pass

class RateLimitError(AIProviderError):
    """Rate limit exceeded, retry after delay"""
    pass

class AuthenticationError(AIProviderError):  
    """Invalid API key or authentication failure"""
    pass

class ModelUnavailableError(AIProviderError):
    """Requested model not available or accessible"""
    pass

class ContentFilterError(AIProviderError):
    """Content filtered by provider safety systems"""
    pass
```

### Fallback Strategy
1. **Primary Provider Failure**: Retry with exponential backoff
2. **Persistent Failure**: Log error and attempt fallback provider
3. **All Providers Failed**: Return user-friendly error with manual override option
4. **Partial Failure**: Process remaining content with available providers

## Acceptance Criteria

### Functional Acceptance
- [ ] Successfully switch between OpenAI, local, and mock providers via environment variables
- [ ] Maintain consistent API interface across all provider implementations
- [ ] Support both text generation and vision processing through unified interface
- [ ] Handle provider-specific errors with appropriate retry and fallback logic
- [ ] Generate consistent quality outputs across comparable models

### Performance Acceptance
- [ ] Text processing completes within 5-second response time requirement
- [ ] Vision processing completes within 10-second response time requirement
- [ ] Rate limiting prevents API quota exhaustion across all providers
- [ ] Connection pooling optimizes resource usage for concurrent requests
- [ ] Error recovery maintains system responsiveness under provider failures

### Quality Acceptance
- [ ] Brand voice analysis produces consistent scoring across providers
- [ ] Generated content maintains quality standards regardless of provider
- [ ] Error messages provide clear guidance for resolution
- [ ] Provider switching occurs seamlessly without data loss
- [ ] Mock provider responses enable reliable testing and development

### Integration Acceptance
- [ ] AI service integrates seamlessly with existing content activation pipeline
- [ ] ActivationLog captures provider metadata for audit and analysis
- [ ] Configuration changes take effect without application restart
- [ ] Provider-specific features (vision, specialized models) work correctly
- [ ] Security requirements met for API key management and data handling

## Extensibility Framework

### Adding New Providers
```python
# Template for new AI provider implementation
class NewProviderAI(AIProvider):
    def __init__(self):
        self.api_key = os.getenv("NEWPROVIDER_API_KEY")
        self.client = NewProviderClient(api_key=self.api_key)
    
    def generate_content(self, prompt: str, context: Dict) -> str:
        # Provider-specific implementation
        pass
    
    def generate_alt_text(self, image_url: str, context: str) -> str:
        # Vision capability implementation (optional)
        pass
    
    def analyze_brand_voice(self, content: str) -> Dict[str, str]:
        # Brand voice analysis implementation
        pass

# Factory update for new provider
def create_service() -> AIProvider:
    provider = os.getenv("AI_PROVIDER", "openai").lower()
    if provider == "newprovider":
        return NewProviderAI()
    # ... existing provider logic
```

### Configuration Extension
- **Environment Variables**: Standard pattern for provider-specific configuration
- **Model Selection**: Configurable model selection within providers
- **Feature Flags**: Enable/disable specific capabilities per provider
- **Performance Tuning**: Provider-specific timeout and retry configuration

## Security Considerations

### API Key Management
- **Environment Variables**: Store all API keys in environment variables
- **Key Rotation**: Support for API key rotation without downtime
- **Access Logging**: Log API access for security monitoring
- **Principle of Least Privilege**: Use minimum required API permissions

### Data Security
- **Request/Response Logging**: Secure logging without exposing sensitive content
- **Data Sanitization**: Validate and sanitize all inputs and outputs
- **Error Message Security**: Avoid exposing sensitive information in errors
- **Provider Isolation**: Prevent cross-provider data leakage

### Compliance Requirements
- **Data Residency**: Consider data residency requirements for different providers
- **Privacy Controls**: Respect privacy settings and content filtering
- **Audit Trail**: Comprehensive logging for compliance and monitoring
- **Content Filtering**: Respect provider content policies and safety measures