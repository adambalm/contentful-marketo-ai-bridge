from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ActivationPayload(BaseModel):
    """
    Pydantic schema for activation requests.
    Represents the complete payload for processing article activation.
    """

    entry_id: str = Field(..., description="Contentful entry ID")
    marketo_list_id: str = Field(..., description="Target Marketo list ID")
    enrichment_enabled: bool = Field(
        True, description="Whether to enable AI enrichment"
    )


class ActivationResult(BaseModel):
    """
    Pydantic schema for activation responses.
    Contains processing results and audit trail data.
    """

    activation_id: str = Field(..., description="Unique activation identifier")
    entry_id: str = Field(..., description="Source Contentful entry ID")
    status: str = Field(..., description="Processing status")
    processing_time: float = Field(..., description="Processing duration in seconds")
    enrichment_data: dict[str, Any] | None = Field(
        None, description="AI enrichment results"
    )
    marketo_response: dict[str, Any] | None = Field(
        None, description="Marketo API response"
    )
    errors: list | None = Field(None, description="Any processing errors")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Processing timestamp"
    )
