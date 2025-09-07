"""
Live Contentful service integration.
Connects to real Contentful CMS with fallback to mock service.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any

import contentful

from .contentful import ContentfulService as MockContentfulService

# Add parent directory to path for secure environment loading
sys.path.insert(0, str(Path(__file__).parent.parent))
from load_env import load_environment

# Load environment variables securely
load_environment()

logger = logging.getLogger(__name__)


class LiveContentfulService:
    """
    Live Contentful service with graceful fallback to mock service.
    Uses real Contentful Delivery API when credentials are available.
    """

    def __init__(self, space_id: str | None = None, access_token: str | None = None):
        self.space_id = space_id or os.getenv("CONTENTFUL_SPACE_ID")
        self.access_token = access_token or os.getenv("CONTENTFUL_ACCESS_TOKEN")
        self.client = None
        self.live_mode = False
        self.mock_service = None

        # Try to initialize live client
        if self.space_id and self.access_token:
            try:
                self.client = contentful.Client(self.space_id, self.access_token)
                # Test connection
                space = self.client.space()
                self.live_mode = True
                logger.info(f"✅ Live Contentful connected to space: {space.name}")
            except Exception as e:
                logger.warning(f"Contentful connection failed, using mock: {e}")
                self.live_mode = False
        else:
            logger.info("Contentful credentials not found, using mock service")
            self.live_mode = False

        # Initialize mock service as fallback
        if not self.live_mode:
            self.mock_service = MockContentfulService()

    def get_article(self, entry_id: str) -> dict[str, Any]:
        """
        Retrieve article from Contentful CMS.
        Falls back to mock service if live connection unavailable.
        """
        if self.live_mode:
            try:
                entry = self.client.entry(entry_id)
                return self._transform_entry(entry)
            except Exception as e:
                logger.error(f"Live Contentful API error: {e}")
                # Fallback to mock
                logger.info("Falling back to mock service")
                if not self.mock_service:
                    self.mock_service = MockContentfulService()
                return self.mock_service.get_article(entry_id)
        else:
            # Use mock service
            if not self.mock_service:
                self.mock_service = MockContentfulService()
            return self.mock_service.get_article(entry_id)

    def _transform_entry(self, entry) -> dict[str, Any]:
        """Transform Contentful entry to expected format matching our ArticleIn schema"""

        # Extract fields with safe attribute access
        fields = {}

        # Required fields
        fields["title"] = getattr(entry, "title", "")
        fields["body"] = getattr(entry, "body", "")
        fields["campaignTags"] = getattr(entry, "campaign_tags", [])

        # Optional fields with our expected names
        fields["summary"] = getattr(
            entry, "ai_summary", None
        )  # Map ai_summary to summary
        fields["aiKeywords"] = getattr(entry, "ai_keywords", [])  # Map ai_keywords
        fields["hasImages"] = getattr(entry, "has_images", False)
        fields["altText"] = getattr(entry, "alt_text", None)
        fields["ctaText"] = getattr(entry, "cta_text", None)
        fields["ctaUrl"] = getattr(entry, "cta_url", None)

        return {"sys": {"id": entry.sys["id"]}, "fields": fields}

    # --- Preserve ActivationLog functionality ---
    def write_activation_log(self, log_record: dict[str, Any]) -> None:
        """
        Write ActivationLog entry to JSONL file.
        Preserves existing functionality regardless of live/mock mode.
        """
        import json
        import os
        from datetime import datetime
        from pathlib import Path

        try:
            # Convert datetime objects to ISO strings for JSON serialization
            def convert_datetimes(obj):
                if isinstance(obj, dict):
                    return {k: convert_datetimes(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetimes(item) for item in obj]
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                else:
                    return obj

            serializable_record = convert_datetimes(log_record)

            log_path = os.getenv("ACTIVATION_LOG_PATH", "activation_logs.jsonl")
            path = Path(log_path)
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(serializable_record) + "\n")
            logger.info(
                f"Activation log written for entry: {serializable_record.get('entry_id')}"
            )
        except Exception as e:
            logger.error(f"Failed to write activation log: {e}")

    def read_latest_activation_log(self, entry_id: str) -> dict[str, Any] | None:
        """
        Read most recent ActivationLog for an entry.
        Preserves existing functionality regardless of live/mock mode.
        """
        import json
        import os
        from pathlib import Path

        log_path = os.getenv("ACTIVATION_LOG_PATH", "activation_logs.jsonl")
        path = Path(log_path)
        if not path.exists():
            return None
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
            for line in reversed(lines):
                try:
                    record = json.loads(line)
                except Exception:
                    continue
                if record.get("entry_id") == entry_id:
                    return record
            return None
        except Exception as e:
            logger.error(f"Failed to read activation log: {e}")
            return None

    def is_live_mode(self) -> bool:
        """Check if service is running in live mode"""
        return self.live_mode
