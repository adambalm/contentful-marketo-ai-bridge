"""
Comprehensive test suite for ai_service.py module.
Tests provider selection, API mocking, error handling, and schema validation.
"""

import os
from unittest.mock import MagicMock

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice

from schemas.enrichment import AIEnrichmentPayload
from services.ai_service import AIService, LocalModelProvider, OpenAIProvider


class TestAIServiceProviderSelection:
    """Test the factory logic for provider selection."""

    def test_ai_service_defaults_to_openai(self, mocker):
        """Test that AIService defaults to OpenAI when no provider specified."""
        mocker.patch.dict(os.environ, {}, clear=True)
        mocker.patch("services.ai_service.OpenAI")  # Mock OpenAI client
        service = AIService()
        assert isinstance(service.provider, OpenAIProvider)

    def test_ai_service_selects_openai_provider(self, mocker):
        """Test that AIService selects OpenAI when AI_PROVIDER=openai."""
        mocker.patch.dict(os.environ, {"AI_PROVIDER": "openai"})
        mocker.patch("services.ai_service.OpenAI")  # Mock OpenAI client
        service = AIService()
        assert isinstance(service.provider, OpenAIProvider)

    def test_ai_service_selects_local_provider(self, mocker):
        """Test that AIService selects local when AI_PROVIDER=local."""
        mocker.patch.dict(os.environ, {"AI_PROVIDER": "local"})
        service = AIService()
        assert isinstance(service.provider, LocalModelProvider)

    def test_ai_service_invalid_provider_defaults_openai(self, mocker, capsys):
        """Test that invalid provider defaults to OpenAI with warning."""
        mocker.patch.dict(os.environ, {"AI_PROVIDER": "invalid_provider"})
        mocker.patch("services.ai_service.OpenAI")  # Mock OpenAI client
        service = AIService()
        assert isinstance(service.provider, OpenAIProvider)

        captured = capsys.readouterr()
        assert "Warning: Unknown AI_PROVIDER 'invalid_provider'" in captured.out


class TestOpenAIProvider:
    """Test the OpenAI provider implementation."""

    def test_openai_provider_successful_enrichment(self, mocker):
        """Test successful OpenAI API call and response parsing."""
        # Mock OpenAI client
        mock_client = MagicMock()
        mocker.patch("services.ai_service.OpenAI", return_value=mock_client)

        # Mock successful API responses
        summary_response = ChatCompletion(
            id="test-1",
            object="chat.completion",
            created=1234567890,
            model="gpt-4o-mini",
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant",
                        content="Discover marketing automation benefits and boost your campaign efficiency today.",
                    ),
                    finish_reason="stop",
                )
            ],
        )

        keywords_response = ChatCompletion(
            id="test-2",
            object="chat.completion",
            created=1234567890,
            model="gpt-4o-mini",
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant",
                        content="marketing, automation, campaign, efficiency, strategy",
                    ),
                    finish_reason="stop",
                )
            ],
        )

        mock_client.chat.completions.create.side_effect = [
            summary_response,
            keywords_response,
        ]

        # Test the provider
        provider = OpenAIProvider()
        article_data = {
            "title": "Marketing Automation Guide",
            "body": "This comprehensive guide covers marketing automation best practices...",
        }

        result = provider.enrich_content(article_data)

        # Validate result is proper Pydantic model
        assert isinstance(result, AIEnrichmentPayload)
        assert result.seo_score == 85
        assert len(result.suggested_meta_description) <= 160
        assert 1 <= len(result.keywords) <= 7
        assert result.keywords == [
            "marketing",
            "automation",
            "campaign",
            "efficiency",
            "strategy",
        ]
        assert result.tone_analysis is not None
        assert result.error is None
        assert result.fallback is None

    def test_openai_provider_api_failure_fallback(self, mocker):
        """Test OpenAI API failure triggers fallback response."""
        # Mock OpenAI client that raises exception
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mocker.patch("services.ai_service.OpenAI", return_value=mock_client)

        provider = OpenAIProvider()
        article_data = {
            "title": "Test Article",
            "body": "Test content for error handling",
        }

        result = provider.enrich_content(article_data)

        # Validate fallback response
        assert isinstance(result, AIEnrichmentPayload)
        assert result.seo_score == 70
        assert result.error is not None
        assert "API Error" in result.error
        assert result.fallback is True
        assert result.keywords == ["marketing", "automation", "strategy"]

    def test_openai_provider_meta_description_length_limit(self, mocker):
        """Test that meta description is truncated to 160 characters."""
        # Mock long summary response
        mock_client = MagicMock()
        mocker.patch("services.ai_service.OpenAI", return_value=mock_client)

        long_summary = "This is a very long meta description that exceeds the 160 character limit and should be truncated to ensure proper SEO compliance and display"

        summary_response = ChatCompletion(
            id="test-1",
            object="chat.completion",
            created=1234567890,
            model="gpt-4o-mini",
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant", content=long_summary
                    ),
                    finish_reason="stop",
                )
            ],
        )

        keywords_response = ChatCompletion(
            id="test-2",
            object="chat.completion",
            created=1234567890,
            model="gpt-4o-mini",
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant", content="test, keywords"
                    ),
                    finish_reason="stop",
                )
            ],
        )

        mock_client.chat.completions.create.side_effect = [
            summary_response,
            keywords_response,
        ]

        provider = OpenAIProvider()
        result = provider.enrich_content({"title": "Test", "body": "Test body"})

        assert len(result.suggested_meta_description) <= 160


class TestLocalModelProvider:
    """Test the local model provider implementation."""

    def test_local_provider_ollama_response(self):
        """Test that LocalModelProvider returns real Ollama response structure."""
        provider = LocalModelProvider()
        article_data = {
            "title": "Test Local Article",
            "body": "Test content for local model",
        }

        result = provider.enrich_content(article_data)

        # Validate response structure for real Ollama
        assert isinstance(result, AIEnrichmentPayload)
        assert result.seo_score == 80  # Ollama baseline
        assert result.readability_score == 75
        assert len(result.suggested_meta_description) <= 160
        assert len(result.keywords) >= 1
        assert result.provider == "ollama"
        assert result.mock is False

    def test_local_provider_schema_compliance(self):
        """Test that LocalModelProvider output validates against schema."""
        provider = LocalModelProvider()
        result = provider.enrich_content({"title": "Schema Test", "body": "Content"})

        # Validate all required fields are present
        assert result.seo_score is not None
        assert result.suggested_meta_description is not None
        assert result.keywords is not None
        assert len(result.keywords) >= 1
        assert len(result.suggested_meta_description) <= 160


class TestAIServiceIntegration:
    """Test the main AIService integration."""

    def test_ai_service_delegates_to_provider(self, mocker):
        """Test that AIService properly delegates to the configured provider."""
        # Mock provider
        mock_provider = MagicMock()
        mock_payload = AIEnrichmentPayload(
            seo_score=90,
            suggested_meta_description="Test response",
            keywords=["test", "integration"],
        )
        mock_provider.enrich_content.return_value = mock_payload

        # Mock AIService to use our mock provider
        mocker.patch.dict(os.environ, {"AI_PROVIDER": "openai"})
        mocker.patch("services.ai_service.OpenAIProvider", return_value=mock_provider)

        service = AIService()
        article_data = {"title": "Test", "body": "Content"}
        result = service.enrich_content(article_data)

        # Validate delegation
        mock_provider.enrich_content.assert_called_once_with(article_data)
        assert result == mock_payload
        assert isinstance(result, AIEnrichmentPayload)


class TestSchemaValidation:
    """Test Pydantic schema validation for all providers."""

    def test_enrichment_payload_validation_success(self):
        """Test valid AIEnrichmentPayload creation."""
        valid_data = {
            "seo_score": 85,
            "suggested_meta_description": "Valid meta description under 160 chars",
            "keywords": ["valid", "keywords", "list"],
        }

        payload = AIEnrichmentPayload(**valid_data)
        assert payload.seo_score == 85
        assert payload.keywords == ["valid", "keywords", "list"]

    def test_enrichment_payload_validation_failure(self):
        """Test invalid AIEnrichmentPayload raises validation error."""
        # Invalid seo_score (out of range)
        with pytest.raises(ValueError):
            AIEnrichmentPayload(
                seo_score=150,  # Invalid: > 100
                suggested_meta_description="Test",
                keywords=["test"],
            )

        # Invalid meta description (too long)
        with pytest.raises(ValueError):
            AIEnrichmentPayload(
                seo_score=85,
                suggested_meta_description="x" * 200,  # Invalid: > 160 chars
                keywords=["test"],
            )

        # Invalid keywords (too many)
        with pytest.raises(ValueError):
            AIEnrichmentPayload(
                seo_score=85,
                suggested_meta_description="Test",
                keywords=["1", "2", "3", "4", "5", "6", "7", "8"],  # Invalid: > 7 items
            )
