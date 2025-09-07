"""
Provider-agnostic AI service for content enrichment.
Supports OpenAI API and future local model providers.
"""

import logging
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Optional

from openai import OpenAI

from schemas.enrichment import AIEnrichmentPayload

from .vision_service import VisionService

logger = logging.getLogger(__name__)


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

    def generate_alt_text_for_images(
        self, article_data: dict[str, Any]
    ) -> Optional[str]:
        """
        Generate alt text for images if present in article.
        Default implementation returns None - providers can override.
        """
        return None

    def _extract_image_urls_from_content(self, content: str) -> list[str]:
        """Extract image URLs from HTML or Markdown content."""
        image_urls = []

        # HTML img tags
        html_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        html_matches = re.findall(html_pattern, content, re.IGNORECASE)
        image_urls.extend(html_matches)

        # Markdown images
        md_pattern = r"!\[([^\]]*)\]\(([^)]+)\)"
        md_matches = re.findall(md_pattern, content)
        image_urls.extend([url for alt, url in md_matches])

        # Contentful asset URLs
        contentful_pattern = r"https://images\.ctfassets\.net/[a-zA-Z0-9]+/[a-zA-Z0-9]+/[a-zA-Z0-9]+/[^?\s]+"
        contentful_matches = re.findall(contentful_pattern, content)
        image_urls.extend(contentful_matches)

        # Filter for valid image URLs
        valid_urls = []
        for url in image_urls:
            if self._is_valid_image_url(url.strip()):
                valid_urls.append(url.strip())

        return valid_urls

    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL is likely an image."""
        if not url:
            return False

        # Check for image extensions
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]
        url_lower = url.lower()

        return any(url_lower.endswith(ext) for ext in image_extensions)

    def _extract_contentful_asset_urls(self, article_data: dict[str, Any]) -> list[str]:
        """Extract image URLs from Contentful Asset fields (featured_image, image_gallery)."""
        urls = []

        # Extract from featured_image field
        featured_image = article_data.get("featured_image")
        if featured_image and hasattr(featured_image, "url"):
            # Call the url() method to get the actual URL string
            url_str = (
                featured_image.url()
                if callable(featured_image.url)
                else featured_image.url
            )
            if url_str:
                urls.append(url_str)

        # Extract from image_gallery field
        image_gallery = article_data.get("image_gallery", [])
        if isinstance(image_gallery, list):
            for asset in image_gallery:
                if hasattr(asset, "url"):
                    # Call the url() method to get the actual URL string
                    url_str = asset.url() if callable(asset.url) else asset.url
                    if url_str:
                        urls.append(url_str)

        return urls


class OpenAIProvider(AIProvider):
    """OpenAI API provider for content enrichment."""

    def __init__(self, api_key: str | None = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            # For testing purposes, use a dummy key
            api_key = "dummy-key-for-testing"
        self.client = OpenAI(api_key=api_key)
        self.vision_service = VisionService(provider="openai")

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

    def generate_alt_text_for_images(
        self, article_data: dict[str, Any]
    ) -> Optional[str]:
        """Generate alt text for images using GPT-4o vision if images are present."""
        # Check both hasImages (camelCase) and has_images (snake_case)
        has_images = article_data.get("hasImages", False) or article_data.get(
            "has_images", False
        )
        if not has_images:
            return None

        # Create context from article
        context = (
            f"{article_data.get('title', '')} - {article_data.get('body', '')[:200]}"
        )

        # Extract image URLs from multiple sources
        image_urls = []

        # 1. Extract from body content (HTML/Markdown embedded images)
        body = article_data.get("body", "")
        body_urls = self._extract_image_urls_from_content(body)
        image_urls.extend(body_urls)

        # 2. Extract from Contentful Asset fields (featured_image, image_gallery)
        contentful_urls = self._extract_contentful_asset_urls(article_data)
        image_urls.extend(contentful_urls)

        if not image_urls:
            logger.warning(
                "Article marked has_images=True but no image URLs found in body or asset fields"
            )
            return None

        # Generate alt text for the first image (could be extended for multiple)
        try:
            image_url = image_urls[0]  # Process first image
            # Ensure URL has protocol (Contentful URLs start with //)
            if image_url.startswith("//"):
                image_url = "https:" + image_url

            alt_text = self.vision_service.generate_alt_text(image_url, context)
            logger.info(f"OpenAI Vision generated alt text for {image_url[:50]}...")
            return alt_text
        except Exception as e:
            logger.error(f"OpenAI Vision processing failed: {e}")
            return "Image description unavailable"


class LocalModelProvider(AIProvider):
    """Ollama local model provider for content enrichment."""

    def __init__(
        self,
        model_name: str = "llama3.2:latest",
        base_url: str = "http://localhost:11434",
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.vision_service = VisionService(provider="qwen")

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

    def generate_alt_text_for_images(
        self, article_data: dict[str, Any]
    ) -> Optional[str]:
        """Generate alt text for images using Qwen 2.5VL 7b if images are present."""
        # Check both hasImages (camelCase) and has_images (snake_case)
        has_images = article_data.get("hasImages", False) or article_data.get(
            "has_images", False
        )
        if not has_images:
            return None

        # Create context from article
        context = (
            f"{article_data.get('title', '')} - {article_data.get('body', '')[:200]}"
        )

        # Extract image URLs from multiple sources
        image_urls = []

        # 1. Extract from body content (HTML/Markdown embedded images)
        body = article_data.get("body", "")
        body_urls = self._extract_image_urls_from_content(body)
        image_urls.extend(body_urls)

        # 2. Extract from Contentful Asset fields (featured_image, image_gallery)
        contentful_urls = self._extract_contentful_asset_urls(article_data)
        image_urls.extend(contentful_urls)

        if not image_urls:
            logger.warning(
                "Article marked has_images=True but no image URLs found in body or asset fields"
            )
            return None

        # Generate alt text for the first image (could be extended for multiple)
        try:
            image_url = image_urls[0]  # Process first image
            # Ensure URL has protocol (Contentful URLs start with //)
            if image_url.startswith("//"):
                image_url = "https:" + image_url

            alt_text = self.vision_service.generate_alt_text(image_url, context)
            logger.info(f"Qwen Vision generated alt text for {image_url[:50]}...")
            return alt_text
        except Exception as e:
            logger.error(f"Qwen Vision processing failed: {e}")
            return "Image description unavailable"


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

    def generate_alt_text(self, article_data: dict[str, Any]) -> Optional[str]:
        """Generate alt text for images if present in article."""
        return self.provider.generate_alt_text_for_images(article_data)
