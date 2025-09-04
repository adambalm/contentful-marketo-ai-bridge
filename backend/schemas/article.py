from pydantic import BaseModel, Field, validator


class ArticleIn(BaseModel):
    """
    Pydantic schema for incoming Contentful articles.
    Validates controlled vocabulary, conditional alt text, and CTA fields.
    """

    title: str = Field(..., max_length=70, description="SEO-optimized title")
    body: str = Field(..., min_length=100, description="Main content body")
    summary: str | None = Field(
        None, max_length=160, description="Optional existing summary"
    )
    campaign_tags: list[str] = Field(
        ..., min_items=1, description="Tags from controlled vocabulary"
    )
    alt_text: str | None = Field(
        None,
        description="Image alt text for accessibility (required if images present)",
    )
    has_images: bool = Field(False, description="Whether article contains images")
    cta_text: str | None = Field(None, max_length=80, description="Call-to-action text")
    cta_url: str | None = Field(None, description="Call-to-action URL")
    content_type: str = Field("article", description="Content type identifier")

    @validator("campaign_tags")
    def validate_controlled_vocabulary(cls, v):
        """Validate campaign tags against controlled vocabulary taxonomy."""
        allowed_tags = {
            # Content Types
            "product-launch",
            "thought-leadership",
            "case-study",
            "webinar",
            "ebook",
            "release-notes",
            "tutorial",
            "whitepaper",
            "demo",
            "blog-post",
            # Audience Segments
            "developer",
            "marketer",
            "enterprise",
            "startup",
            "technical-decision-maker",
            "content-creator",
            "product-manager",
            "executive",
            # Funnel Stages
            "awareness",
            "consideration",
            "decision",
            "retention",
            "advocacy",
            # Campaign Types
            "demand-gen",
            "brand-awareness",
            "product-adoption",
            "customer-success",
            "lead-nurture",
            "competitive-intelligence",
        }
        invalid_tags = set(v) - allowed_tags
        if invalid_tags:
            raise ValueError(
                f"Invalid tags: {invalid_tags}. Must use controlled vocabulary: {sorted(allowed_tags)}"
            )
        return v

    @validator("alt_text")
    def validate_alt_text_when_images_present(cls, v, values):
        """Require alt text when article contains images."""
        has_images = values.get("has_images", False)
        if has_images and not v:
            raise ValueError("Alt text is required when article contains images")
        return v

    @validator("cta_url")
    def validate_cta_url_format(cls, v):
        """Validate CTA URL format."""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("CTA URL must be a valid HTTP/HTTPS URL")
        return v
