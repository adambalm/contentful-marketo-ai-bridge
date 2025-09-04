from pydantic import BaseModel, Field


class AIEnrichmentPayload(BaseModel):
    """
    Pydantic schema for AI enrichment responses.
    Standardizes the structure returned by all AI providers.
    """

    seo_score: int = Field(
        ..., ge=0, le=100, description="SEO optimization score (0-100)"
    )
    readability_score: int | None = Field(
        None, ge=0, le=100, description="Content readability score"
    )
    suggested_meta_description: str = Field(
        ..., max_length=160, description="AI-generated meta description"
    )
    keywords: list[str] = Field(
        ..., min_length=1, max_length=7, description="Extracted keywords (1-7)"
    )
    keyword_density: dict[str, float] | None = Field(
        None, description="Keyword frequency analysis"
    )
    tone_analysis: dict[str, float] | None = Field(
        None, description="Brand voice analysis scores"
    )
    content_gaps: list[str] | None = Field(
        None, description="Suggested content improvements"
    )
    error: str | None = Field(None, description="Error message if enrichment failed")
    fallback: bool | None = Field(None, description="True if using fallback/mock data")
    provider: str | None = Field(None, description="AI provider identifier")
    mock: bool | None = Field(None, description="True if mock/placeholder data")
