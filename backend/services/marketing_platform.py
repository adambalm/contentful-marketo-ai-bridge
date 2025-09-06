"""
Marketing platform factory for switching between different providers.
Supports Marketo, HubSpot, and mock services based on configuration.
"""

import os
import asyncio
from typing import Any, Dict, List

from .marketo import MarketoService
from .hubspot import HubSpotService


class AsyncMarketingAdapter:
    """
    Async adapter that wraps both sync and async marketing services
    with a unified async interface for FastAPI.
    """
    
    def __init__(self, service):
        self.service = service
        self._is_async = hasattr(service, 'add_to_list') and asyncio.iscoroutinefunction(service.add_to_list)
    
    async def add_to_list(self, list_id: str, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Unified async interface for all marketing services."""
        if self._is_async:
            return await self.service.add_to_list(list_id, leads)
        else:
            # Run sync method in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.service.add_to_list, list_id, leads)
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection for all service types."""
        if hasattr(self.service, 'test_connection'):
            if asyncio.iscoroutinefunction(self.service.test_connection):
                return await self.service.test_connection()
            else:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, self.service.test_connection)
        return {"success": True, "platform": "unknown", "message": "No test method available"}


class MockMarketingService:
    """
    Mock marketing service for development and testing.
    Provides consistent interface without external API dependencies.
    """
    
    def __init__(self):
        self.platform = "mock"
        self.mock_lists = {
            "ML_DEMO_001": "Product Launch Prospects",
            "ML_DEMO_002": "Thought Leadership Audience", 
            "ML_DEMO_003": "Developer Community",
            "HS_LIST_001": "HubSpot Marketing Qualified Leads",
            "HS_LIST_002": "Content Engagement Audience"
        }

    def add_to_list(self, list_id: str, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock implementation of list membership addition."""
        import time
        import random
        
        # Simulate realistic API latency
        time.sleep(0.25)
        
        list_name = self.mock_lists.get(list_id, f"Unknown List ({list_id})")
        
        return {
            "requestId": f"mock_request_{random.randint(1000, 9999)}",
            "success": True,
            "result": [
                {"id": i + 1, "status": "added", "email": lead.get("email", f"demo-{i}@example.com")} 
                for i, lead in enumerate(leads)
            ],
            "list_id": list_id,
            "list_name": list_name,
            "contacts_processed": len(leads),
            "platform": "mock",
            "mock_mode": True,
            "simulated_latency_ms": 250
        }

    def test_connection(self) -> Dict[str, Any]:
        """Mock connection test."""
        return {
            "success": True,
            "platform": "mock",
            "message": "Mock service connection successful"
        }


class MarketingPlatformFactory:
    """
    Factory class for creating marketing platform service instances.
    Handles environment-based switching between providers.
    """
    
    @staticmethod
    def create_service() -> AsyncMarketingAdapter:
        """
        Create appropriate marketing service based on environment configuration.
        
        Returns:
            AsyncMarketingAdapter wrapping the configured service
        """
        platform = os.getenv("MARKETING_PLATFORM", "mock").lower()
        
        if platform == "marketo":
            service = MarketingPlatformFactory._create_marketo_service()
        elif platform == "hubspot":
            service = MarketingPlatformFactory._create_hubspot_service()
        elif platform == "mock":
            service = MockMarketingService()
        else:
            print(f"Warning: Unknown MARKETING_PLATFORM '{platform}', defaulting to mock service")
            service = MockMarketingService()
            
        return AsyncMarketingAdapter(service)

    @staticmethod
    def _create_marketo_service() -> MarketoService:
        """Create Marketo service with environment configuration."""
        try:
            return MarketoService(
                client_id=os.getenv("MARKETO_CLIENT_ID"),
                client_secret=os.getenv("MARKETO_CLIENT_SECRET"), 
                munchkin_id=os.getenv("MARKETO_MUNCHKIN_ID")
            )
        except Exception as e:
            print(f"Warning: Failed to initialize Marketo service: {e}")
            print("Falling back to mock service")
            return MockMarketingService()

    @staticmethod
    def _create_hubspot_service() -> HubSpotService:
        """Create HubSpot service with environment configuration."""
        try:
            return HubSpotService(
                access_token=os.getenv("HUBSPOT_ACCESS_TOKEN"),
                portal_id=os.getenv("HUBSPOT_PORTAL_ID")
            )
        except Exception as e:
            print(f"Warning: Failed to initialize HubSpot service: {e}")
            print("Falling back to mock service")
            return MockMarketingService()

    @staticmethod
    def get_platform_info() -> Dict[str, Any]:
        """Get information about the configured marketing platform."""
        platform = os.getenv("MARKETING_PLATFORM", "mock").lower()
        
        platform_info = {
            "marketo": {
                "name": "Marketo",
                "description": "Enterprise marketing automation platform",
                "setup_complexity": "High (requires sandbox approval)",
                "api_docs": "https://developers.marketo.com/rest-api/"
            },
            "hubspot": {
                "name": "HubSpot",
                "description": "Accessible marketing automation with free tier",
                "setup_complexity": "Low (free developer account)",
                "api_docs": "https://developers.hubspot.com/docs/api/overview"
            },
            "mock": {
                "name": "Mock Service",
                "description": "Development/testing service with simulated responses",
                "setup_complexity": "None (no external dependencies)",
                "api_docs": "Built-in mock implementation"
            }
        }
        
        return {
            "current_platform": platform,
            "platform_details": platform_info.get(platform, platform_info["mock"]),
            "available_platforms": list(platform_info.keys())
        }