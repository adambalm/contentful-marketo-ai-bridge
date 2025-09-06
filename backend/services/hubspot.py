"""
HubSpot service for marketing automation integration.
More accessible alternative to Marketo with simpler API setup.
"""

import os
import httpx
from typing import Any, Dict, List


class HubSpotService:
    """
    HubSpot API integration for contact management and list operations.
    Provides simpler setup compared to Marketo sandbox requirements.
    """

    def __init__(
        self,
        access_token: str | None = None,
        portal_id: str | None = None,
    ):
        self.access_token = access_token or os.getenv("HUBSPOT_ACCESS_TOKEN")
        self.portal_id = portal_id or os.getenv("HUBSPOT_PORTAL_ID")
        self.base_url = "https://api.hubapi.com"
        
        if not self.access_token:
            raise ValueError("HubSpot access token is required")

    async def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make authenticated async request to HubSpot API."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=headers, json=data)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                    
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"HubSpot API error: {str(e)}",
                "status_code": getattr(e.response, "status_code", None) if hasattr(e, "response") else None
            }

    async def create_or_update_contact(self, email: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a contact in HubSpot.
        
        Args:
            email: Contact email address (primary identifier)
            properties: Contact properties (firstname, lastname, etc.)
            
        Returns:
            API response with contact ID and status
        """
        contact_data = {
            "properties": {
                "email": email,
                **properties
            }
        }
        
        # Try to create contact first
        result = await self._make_request("POST", "/crm/v3/objects/contacts", contact_data)
        
        if result.get("success") is False and "already exists" in str(result.get("error", "")):
            # Contact exists, update instead
            contact_id = await self._get_contact_by_email(email)
            if contact_id:
                return await self._make_request("PUT", f"/crm/v3/objects/contacts/{contact_id}", contact_data)
        
        return result

    async def _get_contact_by_email(self, email: str) -> str | None:
        """Get contact ID by email address."""
        search_data = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "email",
                            "operator": "EQ",
                            "value": email
                        }
                    ]
                }
            ]
        }
        
        result = await self._make_request("POST", "/crm/v3/objects/contacts/search", search_data)
        
        if result.get("results"):
            return result["results"][0]["id"]
        return None

    async def add_contact_to_list(self, list_id: str, contact_emails: List[str]) -> Dict[str, Any]:
        """
        Add contacts to a static list in HubSpot.
        
        Args:
            list_id: HubSpot static list ID
            contact_emails: List of email addresses to add
            
        Returns:
            API response with success status and contact IDs
        """
        contact_ids = []
        
        # First ensure all contacts exist
        for email in contact_emails:
            contact_result = await self.create_or_update_contact(email, {
                "firstname": "Demo",
                "lastname": "Contact",
                "lifecyclestage": "lead"
            })
            
            if contact_result.get("id"):
                contact_ids.append(contact_result["id"])
        
        # Add contacts to list
        if contact_ids:
            list_data = {
                "memberships": [
                    {"contact-id": contact_id} for contact_id in contact_ids
                ]
            }
            
            return await self._make_request("PUT", f"/contacts/v1/lists/{list_id}/add", list_data)
        
        return {
            "success": False,
            "error": "No valid contacts to add to list"
        }

    async def add_to_list(self, list_id: str, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Marketo-compatible interface for adding leads to lists.
        Maps lead data to HubSpot contact properties.
        
        Args:
            list_id: HubSpot static list ID
            leads: List of lead dictionaries with email, firstName, lastName, etc.
            
        Returns:
            Response compatible with Marketo service interface
        """
        try:
            processed_contacts = []
            
            for lead in leads:
                email = lead.get("email")
                if not email:
                    continue
                    
                properties = {
                    "firstname": lead.get("firstName", "Demo"),
                    "lastname": lead.get("lastName", "Lead"),
                    "lifecyclestage": "lead"
                }
                
                # Map additional fields from content activation
                if lead.get("contentTitle"):
                    properties["last_content_engaged"] = lead["contentTitle"]
                if lead.get("campaignTags"):
                    properties["campaign_tags"] = lead["campaignTags"]
                
                contact_result = await self.create_or_update_contact(email, properties)
                
                if contact_result.get("id"):
                    processed_contacts.append({
                        "id": contact_result["id"],
                        "email": email,
                        "status": "processed"
                    })
            
            # Add to list if we have contacts
            if processed_contacts:
                contact_emails = [c["email"] for c in processed_contacts]
                list_result = await self.add_contact_to_list(list_id, contact_emails)
                
                return {
                    "requestId": f"hubspot_activation_{list_id}",
                    "success": list_result.get("success", True),
                    "result": processed_contacts,
                    "contacts_processed": len(processed_contacts),
                    "list_id": list_id,
                    "platform": "hubspot"
                }
            
            return {
                "requestId": f"hubspot_activation_{list_id}",
                "success": False,
                "error": "No valid contacts to process",
                "platform": "hubspot"
            }
            
        except Exception as e:
            return {
                "requestId": f"hubspot_activation_{list_id}",
                "success": False,
                "error": f"HubSpot integration error: {str(e)}",
                "platform": "hubspot"
            }

    async def get_lists(self) -> Dict[str, Any]:
        """Get available static lists for contact management."""
        return await self._make_request("GET", "/contacts/v1/lists/static")

    async def test_connection(self) -> Dict[str, Any]:
        """Test HubSpot API connection and credentials."""
        result = await self._make_request("GET", "/crm/v3/objects/contacts?limit=1")
        
        return {
            "success": result.get("success", True) if "error" not in result else False,
            "platform": "hubspot",
            "portal_id": self.portal_id,
            "message": "Connection successful" if "error" not in result else result.get("error")
        }