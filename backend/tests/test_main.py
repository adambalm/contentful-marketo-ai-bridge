import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Set environment before importing app
os.environ["AI_PROVIDER"] = "local"

from main import app
from schemas.enrichment import AIEnrichmentPayload


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def valid_activation_payload():
    """Valid activation request payload."""
    return {
        "entry_id": "test-entry-123",
        "marketo_list_id": "ML_TEST_001",
        "enrichment_enabled": True,
    }


@pytest.fixture
def mock_article_data():
    """Mock article data from Contentful."""
    return {
        "sys": {"id": "test-entry-123"},
        "fields": {
            "title": "Test Marketing Article",
            "body": "This is a comprehensive test article about marketing automation and its benefits for modern businesses. Marketing automation platforms help streamline workflows.",
            "summary": "Test article summary under 160 characters",
            "campaignTags": ["thought-leadership", "marketer", "awareness"],
            "hasImages": True,
            "altText": "Marketing automation dashboard interface",
            "ctaText": "Get Started",
            "ctaUrl": "https://example.com/get-started",
        },
    }


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


class TestActivateEndpoint:
    """Comprehensive tests for the /activate endpoint."""

    def test_activate_success_with_enrichment(
        self, client, valid_activation_payload, mock_article_data
    ):
        """Test successful activation with AI enrichment enabled."""
        mock_enrichment = AIEnrichmentPayload(
            seo_score=88,
            suggested_meta_description="Test article about marketing automation benefits and strategies",
            keywords=["marketing", "automation", "strategy"],
        )

        with (
            patch(
                "main.contentful_service.get_article", return_value=mock_article_data
            ),
            patch("main.ai_service.enrich_content", return_value=mock_enrichment),
            patch(
                "main.marketing_service.add_to_list",
                return_value={"success": True, "leads_added": 1},
            ),
        ):
            response = client.post("/activate", json=valid_activation_payload)

            assert response.status_code == 200
            data = response.json()

            # Validate response structure
            assert data["status"] == "success"
            assert data["entry_id"] == "test-entry-123"
            assert "activation_id" in data
            assert "processing_time" in data
            assert data["enrichment_data"] is not None
            assert data["marketo_response"] is not None
            assert data["errors"] is None

    def test_activate_success_without_enrichment(self, client, mock_article_data):
        """Test successful activation with AI enrichment disabled."""
        payload = {
            "entry_id": "test-entry-123",
            "marketo_list_id": "ML_TEST_001",
            "enrichment_enabled": False,
        }

        with (
            patch(
                "main.contentful_service.get_article", return_value=mock_article_data
            ),
            patch(
                "main.marketing_service.add_to_list",
                return_value={"success": True, "leads_added": 1},
            ),
        ):
            response = client.post("/activate", json=payload)

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "success"
            assert data["enrichment_data"] is None  # No enrichment when disabled
            assert data["marketo_response"] is not None

    def test_activate_validation_failure_missing_alt_text(self, client):
        """Test activation fails when alt text is missing but images are present."""
        invalid_article = {
            "sys": {"id": "test-entry-123"},
            "fields": {
                "title": "Test Article",
                "body": "This is a test article with sufficient length to meet validation requirements.",
                "campaignTags": ["thought-leadership", "marketer"],
                "hasImages": True,
                # Missing altText - should cause validation failure
                "ctaText": "Learn More",
                "ctaUrl": "https://example.com/learn-more",
            },
        }

        with patch("main.contentful_service.get_article", return_value=invalid_article):
            response = client.post(
                "/activate",
                json={
                    "entry_id": "test-entry-123",
                    "marketo_list_id": "ML_TEST_001",
                    "enrichment_enabled": True,
                },
            )

            assert response.status_code == 400
            assert "validation failed" in response.json()["detail"].lower()

    def test_activate_validation_failure_invalid_campaign_tags(self, client):
        """Test activation fails with invalid campaign tags."""
        invalid_article = {
            "sys": {"id": "test-entry-123"},
            "fields": {
                "title": "Test Article",
                "body": "This is a test article with sufficient length to meet validation requirements.",
                "campaignTags": ["invalid-tag", "another-invalid-tag"],  # Invalid tags
                "hasImages": False,
                "ctaText": "Learn More",
                "ctaUrl": "https://example.com/learn-more",
            },
        }

        with patch("main.contentful_service.get_article", return_value=invalid_article):
            response = client.post(
                "/activate",
                json={
                    "entry_id": "test-entry-123",
                    "marketo_list_id": "ML_TEST_001",
                    "enrichment_enabled": True,
                },
            )

            assert response.status_code == 400
            assert "validation failed" in response.json()["detail"].lower()

    def test_activate_validation_failure_invalid_cta_url(self, client):
        """Test activation fails with invalid CTA URL format."""
        invalid_article = {
            "sys": {"id": "test-entry-123"},
            "fields": {
                "title": "Test Article",
                "body": "This is a test article with sufficient length to meet validation requirements.",
                "campaignTags": ["thought-leadership", "marketer"],
                "hasImages": False,
                "ctaText": "Learn More",
                "ctaUrl": "invalid-url-format",  # Invalid URL format
            },
        }

        with patch("main.contentful_service.get_article", return_value=invalid_article):
            response = client.post(
                "/activate",
                json={
                    "entry_id": "test-entry-123",
                    "marketo_list_id": "ML_TEST_001",
                    "enrichment_enabled": True,
                },
            )

            assert response.status_code == 400
            assert "validation failed" in response.json()["detail"].lower()

    def test_activate_contentful_service_failure(
        self, client, valid_activation_payload
    ):
        """Test activation handles Contentful service failure gracefully."""
        with patch(
            "main.contentful_service.get_article",
            side_effect=Exception("Contentful API error"),
        ):
            response = client.post("/activate", json=valid_activation_payload)

            assert (
                response.status_code == 200
            )  # Still returns 200 but with error status
            data = response.json()
            assert data["status"] == "error"
            assert data["errors"] is not None
            assert any("Contentful API error" in str(error) for error in data["errors"])

    def test_activate_ai_service_failure_continues(
        self, client, valid_activation_payload, mock_article_data
    ):
        """Test activation continues when AI service fails (graceful degradation)."""
        with (
            patch(
                "main.contentful_service.get_article", return_value=mock_article_data
            ),
            patch(
                "main.ai_service.enrich_content",
                side_effect=Exception("OpenAI API error"),
            ),
            patch("main.marketing_service.add_to_list", return_value={"success": True}),
        ):
            response = client.post("/activate", json=valid_activation_payload)

            # Should still complete successfully without enrichment
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"  # Will be error due to AI failure
            assert data["errors"] is not None

    def test_activate_marketo_service_failure_continues(
        self, client, valid_activation_payload, mock_article_data
    ):
        """Test activation handles Marketo service failure gracefully."""
        mock_enrichment = AIEnrichmentPayload(
            seo_score=85,
            suggested_meta_description="Test meta description",
            keywords=["test", "keywords"],
        )

        with (
            patch(
                "main.contentful_service.get_article", return_value=mock_article_data
            ),
            patch("main.ai_service.enrich_content", return_value=mock_enrichment),
            patch(
                "main.marketing_service.add_to_list",
                side_effect=Exception("Marketo API error"),
            ),
        ):
            response = client.post("/activate", json=valid_activation_payload)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"
            assert data["errors"] is not None
            assert any("Marketo API error" in str(error) for error in data["errors"])

    def test_activate_missing_request_fields(self, client):
        """Test activation fails with missing required fields."""
        incomplete_payload = {
            "entry_id": "test-entry-123"
            # Missing marketo_list_id and enrichment_enabled
        }

        response = client.post("/activate", json=incomplete_payload)
        assert response.status_code == 422  # Pydantic validation error

    def test_activate_performance_timing(
        self, client, valid_activation_payload, mock_article_data
    ):
        """Test that activation includes processing time in response."""
        with (
            patch(
                "main.contentful_service.get_article", return_value=mock_article_data
            ),
            patch(
                "main.ai_service.enrich_content",
                return_value=AIEnrichmentPayload(
                    seo_score=85, suggested_meta_description="Test", keywords=["test"]
                ),
            ),
            patch("main.marketing_service.add_to_list", return_value={"success": True}),
        ):
            response = client.post("/activate", json=valid_activation_payload)

            assert response.status_code == 200
            data = response.json()
            assert "processing_time" in data
            assert isinstance(data["processing_time"], float)
            assert data["processing_time"] > 0
