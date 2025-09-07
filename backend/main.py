import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request

from schemas.activation import ActivationPayload, ActivationResult
from schemas.article import ArticleIn
from services.ai_service import AIService
from services.live_contentful import LiveContentfulService
from services.marketing_platform import MarketingPlatformFactory

app = FastAPI(title="Portfolio Backend API", version="1.0.0")

contentful_service = LiveContentfulService()
marketing_service = MarketingPlatformFactory.create_service()
ai_service = AIService()

# Simple in-memory rate limiting (token bucket per client IP)
_RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_RPM", "10"))
_RATE_LIMIT_WINDOW_SEC = 60
_client_requests: dict[str, list[float]] = {}


def _is_rate_limited(client_ip: str) -> bool:
    now = time.time()
    window_start = now - _RATE_LIMIT_WINDOW_SEC
    history = _client_requests.get(client_ip, [])
    # Drop old timestamps
    history = [t for t in history if t >= window_start]
    if len(history) >= _RATE_LIMIT_MAX_REQUESTS:
        _client_requests[client_ip] = history
        return True
    history.append(now)
    _client_requests[client_ip] = history
    return False


def append_activation_log(result: ActivationResult) -> None:
    """Append activation result as JSONL for simple audit logging.

    Controlled via env var ACTIVATION_LOG_PATH (defaults to 'activation_logs.jsonl').
    Failures are swallowed to avoid breaking the main flow.
    """
    try:
        log_path = os.getenv("ACTIVATION_LOG_PATH", "activation_logs.jsonl")
        path = Path(log_path)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(result.model_dump_json() + "\n")
    except Exception:
        # Non-fatal logging failure
        pass


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/platform")
async def get_platform_info():
    """Get information about the configured marketing platform."""
    return MarketingPlatformFactory.get_platform_info()


@app.post("/activate", response_model=ActivationResult)
async def activate_content(payload: ActivationPayload, request: Request):
    """
    Process content activation from Contentful to Marketo with AI enrichment.
    Core endpoint demonstrating marketing automation workflow.
    """
    start_time = time.time()
    activation_id = str(uuid.uuid4())
    errors = []

    try:
        # Rate limit per client IP
        client_ip = request.client.host if request and request.client else "unknown"
        if _is_rate_limited(client_ip):
            raise HTTPException(
                status_code=429, detail="Rate limit exceeded. Please retry later."
            )
        # Step 1: Retrieve article from Contentful
        raw_article = contentful_service.get_article(payload.entry_id)

        # Step 2: Validate against Pydantic schema
        try:
            article = ArticleIn(
                title=raw_article["fields"]["title"],
                body=raw_article["fields"]["body"],
                summary=raw_article["fields"].get("summary"),
                campaign_tags=raw_article["fields"]["campaignTags"],
                alt_text=raw_article["fields"].get("altText"),
                has_images=raw_article["fields"].get("hasImages", False),
                cta_text=raw_article["fields"].get("ctaText"),
                cta_url=raw_article["fields"].get("ctaUrl"),
            )
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            raise HTTPException(
                status_code=400, detail=f"Article validation failed: {str(e)}"
            ) from e

        # Step 3: AI enrichment (if enabled)
        enrichment_data = None
        generated_alt_text = None
        if payload.enrichment_enabled:
            enrichment_result = ai_service.enrich_content(article.model_dump())
            enrichment_data = enrichment_result.model_dump()

            # Generate alt text for images if present
            if article.has_images and not article.alt_text:
                generated_alt_text = ai_service.generate_alt_text(article.model_dump())
                if generated_alt_text:
                    enrichment_data["generated_alt_text"] = generated_alt_text

            # --- Brand-voice advisory mapping ---
            tone = enrichment_data.get("tone_analysis") or {}
            professionalism = float(tone.get("professional", 0))
            confident = float(tone.get("confident", 0))
            action_oriented = float(tone.get("action_oriented", 0))

            def advisory(score: float) -> str:
                # Simple thresholds for MVP
                if score >= 0.8:
                    return "pass"
                if score >= 0.6:
                    return "advisory"
                return "attention"

            enrichment_data["brand_voice"] = {
                "professionalism": advisory(professionalism),
                "confidence": advisory(confident),
                "action_orientation": advisory(action_oriented),
                "overall": advisory(
                    (professionalism + confident + action_oriented) / 3.0
                ),
            }

        # Step 4: Add to Marketo list
        marketo_leads = [
            {
                "email": f"demo-{activation_id}@example.com",
                "firstName": "Demo",
                "lastName": "Lead",
                "contentTitle": article.title,
                "campaignTags": ",".join(article.campaign_tags),
            }
        ]

        marketing_response = await marketing_service.add_to_list(
            payload.marketo_list_id, marketo_leads
        )

        processing_time = time.time() - start_time

        result = ActivationResult(
            activation_id=activation_id,
            entry_id=payload.entry_id,
            status="success",
            processing_time=processing_time,
            enrichment_data=enrichment_data,
            marketo_response=marketing_response,
            errors=errors if errors else None,
            timestamp=datetime.now(timezone.utc),
        )
        append_activation_log(result)
        # Also write to Contentful (mock impl appends to JSONL for MVP)
        try:
            contentful_service.write_activation_log(result.model_dump())
        except Exception:
            pass
        return result

    except HTTPException:
        raise
    except Exception as e:
        errors.append(f"Processing error: {str(e)}")
        processing_time = time.time() - start_time

        result = ActivationResult(
            activation_id=activation_id,
            entry_id=payload.entry_id,
            status="error",
            processing_time=processing_time,
            enrichment_data=None,
            marketo_response=None,
            errors=errors,
            timestamp=datetime.now(timezone.utc),
        )
        append_activation_log(result)
        try:
            contentful_service.write_activation_log(result.model_dump())
        except Exception:
            pass
        return result


@app.get("/activation-log/{entry_id}")
async def get_latest_activation_log(entry_id: str):
    """Return most recent activation log for a given Contentful entry ID (MVP)."""
    record = contentful_service.read_latest_activation_log(entry_id)
    if not record:
        raise HTTPException(status_code=404, detail="No activation log found")
    return record
