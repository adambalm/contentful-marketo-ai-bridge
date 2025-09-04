"""
Mock Contentful service for MVP demonstration.
Simulates article retrieval from Contentful CMS.
"""

from typing import Any


class ContentfulService:
    """
    Mock service simulating Contentful CMS integration.
    Returns hardcoded article data for demonstration.
    """

    def __init__(self, api_token: str | None = None, space_id: str | None = None):
        self.api_token = api_token or "mock_token"
        self.space_id = space_id or "mock_space"

    def get_article(self, entry_id: str) -> dict[str, Any]:
        """
        Mock method to retrieve article from Contentful.
        Returns sample article data for demonstration.
        """
        return {
            "sys": {"id": entry_id},
            "fields": {
                "title": "Sample Marketing Article",
                "body": "This is a sample article body with sufficient length to meet validation requirements. Marketing automation is transforming how businesses engage with prospects and customers across the entire lifecycle.",
                "summary": "Brief overview of marketing automation benefits",
                "campaignTags": ["thought-leadership", "marketer", "awareness"],
                "hasImages": True,
                "altText": "Marketing automation dashboard screenshot",
                "ctaText": "Learn More",
                "ctaUrl": "https://example.com/learn-more",
            },
        }
