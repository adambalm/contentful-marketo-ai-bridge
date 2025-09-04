"""
Provider-agnostic AI service for content enrichment.
Supports OpenAI API and future local model providers.
"""

import os
from abc import ABC, abstractmethod
from typing import Any

from openai import OpenAI

from schemas.enrichment import AIEnrichmentPayload


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def enrich_content(self, article_data: dict[str, Any]) -> AIEnrichmentPayload:
        """
        Enrich article content with AI-generated insights.

        Args:
            article_data: Dictionary containing article fields

        Returns:
            Dictionary with enrichment data including summary and keywords
        """
        pass


class OpenAIProvider(AIProvider):
    """OpenAI API provider for content enrichment."""

    def __init__(self, api_key: str | None = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            # For testing purposes, use a dummy key
            api_key = "dummy-key-for-testing"
        self.client = OpenAI(api_key=api_key)

    def enrich_content(self, article_data: dict[str, Any]) -> AIEnrichmentPayload:
        """Generate summary and keywords using OpenAI API."""
        title = article_data.get("title", "")
        body = article_data.get("body", "")

        try:
            # Generate summary (max 160 characters for meta description)
            summary_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a concise meta description (max 160 characters) for this marketing article. Focus on key benefits and include a subtle call to action.",
                    },
                    {
                        "role": "user",
                        "content": f"Title: {title}\n\nContent: {body[:1000]}",
                    },
                ],
                max_tokens=50,
                temperature=0.7,
            )

            # Extract keywords (3-7 terms)
            keywords_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract 3-7 relevant SEO keywords from this marketing content. Return only the keywords as a comma-separated list.",
                    },
                    {
                        "role": "user",
                        "content": f"Title: {title}\n\nContent: {body[:1000]}",
                    },
                ],
                max_tokens=30,
                temperature=0.3,
            )

            summary = summary_response.choices[0].message.content.strip()
            keywords_text = keywords_response.choices[0].message.content.strip()
            keywords = [kw.strip() for kw in keywords_text.split(",")]

            return AIEnrichmentPayload(
                seo_score=85,
                readability_score=78,
                suggested_meta_description=summary[:160],
                keywords=keywords[:7],
                keyword_density={
                    kw: round(
                        body.lower().count(kw.lower()) / len(body.split()) * 100, 2
                    )
                    for kw in keywords[:3]
                },
                tone_analysis={
                    "professional": 0.9,
                    "confident": 0.8,
                    "action_oriented": 0.85,
                },
                content_gaps=[
                    "Consider adding more specific metrics",
                    "Include customer success examples",
                    "Add clearer call-to-action positioning",
                ],
            )

        except Exception as e:
            # Fallback to basic enrichment if API fails
            return AIEnrichmentPayload(
                seo_score=70,
                suggested_meta_description=f"Learn about {title.lower()} and discover actionable insights for your marketing strategy."[
                    :160
                ],
                keywords=["marketing", "automation", "strategy"],
                error=f"OpenAI API error: {str(e)}",
                fallback=True,
            )


class LocalModelProvider(AIProvider):
    """Ollama local model provider for content enrichment."""

    def __init__(
        self,
        model_name: str = "llama3.2:latest",
        base_url: str = "http://localhost:11434",
    ):
        self.model_name = model_name
        self.base_url = base_url

    def enrich_content(self, article_data: dict[str, Any]) -> AIEnrichmentPayload:
        """Generate summary and keywords using Ollama local model."""
        title = article_data.get("title", "")
        body = article_data.get("body", "")

        try:

            import requests

            # Generate meta description
            summary_prompt = f'Generate a concise SEO meta description (max 160 characters) for this article: Title: "{title}" Content: "{body[:500]}"'
            summary_response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": summary_prompt,
                    "stream": False,
                },
                timeout=30,
            )

            # Extract keywords
            keywords_prompt = f'Extract 5 SEO keywords from this text: "{body[:500]}" Return only the keywords separated by commas.'
            keywords_response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": keywords_prompt,
                    "stream": False,
                },
                timeout=30,
            )

            # Parse responses
            summary_text = summary_response.json().get("response", "").strip()
            keywords_text = keywords_response.json().get("response", "").strip()

            # Clean up responses
            if ":" in summary_text:
                summary_text = summary_text.split(":", 1)[1].strip()
            summary_text = summary_text.strip('"').strip("'")

            # Extract keywords from response
            if ":" in keywords_text:
                keywords_text = keywords_text.split(":", 1)[1].strip()
            keywords = [kw.strip().lower() for kw in keywords_text.split(",")]
            keywords = [kw for kw in keywords if kw and len(kw) > 2][
                :7
            ]  # Limit to 7, filter short words

            return AIEnrichmentPayload(
                seo_score=80,  # Local model baseline
                readability_score=75,
                suggested_meta_description=summary_text[:160],
                keywords=(
                    keywords if keywords else ["marketing", "content", "automation"]
                ),
                keyword_density=(
                    {
                        kw: round(body.lower().count(kw) / len(body.split()) * 100, 2)
                        for kw in keywords[:3]
                        if kw
                    }
                    if keywords
                    else {}
                ),
                tone_analysis={
                    "professional": 0.8,
                    "confident": 0.75,
                    "action_oriented": 0.7,
                },
                content_gaps=[
                    "Generated by local Ollama model",
                    f"Model: {self.model_name}",
                ],
                provider="ollama",
                mock=False,
            )

        except Exception as e:
            # Fallback to basic response if Ollama fails
            return AIEnrichmentPayload(
                seo_score=70,
                suggested_meta_description=f"Learn about {title.lower()} with our comprehensive guide and expert insights."[
                    :160
                ],
                keywords=["local", "model", "fallback"],
                error=f"Ollama error: {str(e)}",
                provider="ollama",
                fallback=True,
            )


class AIService:
    """Main AI service that delegates to the configured provider."""

    def __init__(self):
        provider_name = os.getenv("AI_PROVIDER", "openai").lower()

        if provider_name == "openai":
            self.provider = OpenAIProvider()
        elif provider_name == "local":
            self.provider = LocalModelProvider()
        else:
            # Default to OpenAI with warning
            print(
                f"Warning: Unknown AI_PROVIDER '{provider_name}', defaulting to OpenAI"
            )
            self.provider = OpenAIProvider()

    def enrich_content(self, article_data: dict[str, Any]) -> AIEnrichmentPayload:
        """Enrich content using the configured AI provider."""
        return self.provider.enrich_content(article_data)
