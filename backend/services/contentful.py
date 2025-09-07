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

    # --- MVP ActivationLog mock (JSONL-backed) ---
    def write_activation_log(self, log_record: dict[str, Any]) -> None:
        """
        Mock method to write an ActivationLog entry.
        For MVP, append to the same JSONL file used by backend audit logs.
        Controlled by env var ACTIVATION_LOG_PATH.
        """
        import os
        from pathlib import Path

        try:
            log_path = os.getenv("ACTIVATION_LOG_PATH", "activation_logs.jsonl")
            path = Path(log_path)
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                import json

                f.write(json.dumps(log_record) + "\n")
        except Exception:
            # Non-fatal logging failure
            pass

    def read_latest_activation_log(self, entry_id: str) -> dict[str, Any] | None:
        """
        Mock method to fetch the most recent ActivationLog for an entry.
        Scans the JSONL file from end to beginning for performance in small files.
        """
        import json
        import os
        from pathlib import Path

        log_path = os.getenv("ACTIVATION_LOG_PATH", "activation_logs.jsonl")
        path = Path(log_path)
        if not path.exists():
            return None
        try:
            # Read all lines and scan from the end (files are small in MVP)
            lines = path.read_text(encoding="utf-8").splitlines()
            for line in reversed(lines):
                try:
                    record = json.loads(line)
                except Exception:
                    continue
                if record.get("entry_id") == entry_id:
                    return record
            return None
        except Exception:
            return None
