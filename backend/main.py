import time
import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException

from schemas.activation import ActivationPayload, ActivationResult
from schemas.article import ArticleIn
from services.ai_service import AIService
from services.contentful import ContentfulService
from services.marketo import MarketoService

app = FastAPI(title="Portfolio Backend API", version="1.0.0")

contentful_service = ContentfulService()
marketo_service = MarketoService()
ai_service = AIService()


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/activate", response_model=ActivationResult)
async def activate_content(payload: ActivationPayload):
    """
    Process content activation from Contentful to Marketo with AI enrichment.
    Core endpoint demonstrating marketing automation workflow.
    """
    start_time = time.time()
    activation_id = str(uuid.uuid4())
    errors = []

    try:
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
        if payload.enrichment_enabled:
            enrichment_result = ai_service.enrich_content(article.dict())
            enrichment_data = enrichment_result.dict()

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

        marketo_response = marketo_service.add_to_list(
            payload.marketo_list_id, marketo_leads
        )

        processing_time = time.time() - start_time

        return ActivationResult(
            activation_id=activation_id,
            entry_id=payload.entry_id,
            status="success",
            processing_time=processing_time,
            enrichment_data=enrichment_data,
            marketo_response=marketo_response,
            errors=errors if errors else None,
            timestamp=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        errors.append(f"Processing error: {str(e)}")
        processing_time = time.time() - start_time

        return ActivationResult(
            activation_id=activation_id,
            entry_id=payload.entry_id,
            status="error",
            processing_time=processing_time,
            enrichment_data=None,
            marketo_response=None,
            errors=errors,
            timestamp=datetime.utcnow(),
        )
