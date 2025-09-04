"""
Mock Marketo service for MVP demonstration.
Simulates adding leads to Marketo lists.
"""

from typing import Any


class MarketoService:
    """
    Mock service simulating Marketo REST API integration.
    Returns success responses for demonstration.
    """

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        munchkin_id: str | None = None,
    ):
        self.client_id = client_id or "mock_client_id"
        self.client_secret = client_secret or "mock_client_secret"
        self.munchkin_id = munchkin_id or "mock_munchkin"

    def add_to_list(self, _list_id: str, leads: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Mock method to add leads to Marketo list.
        Returns success response for demonstration.
        """
        return {
            "requestId": "mock_request_123",
            "success": True,
            "result": [{"id": i + 1, "status": "added"} for i, _ in enumerate(leads)],
        }
