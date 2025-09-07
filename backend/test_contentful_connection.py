#!/usr/bin/env python3
"""
Test Contentful API connection and explore existing content
"""

import os

import contentful
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_contentful_connection():
    """Test connection to Contentful and list existing content types"""

    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    access_token = os.getenv("CONTENTFUL_ACCESS_TOKEN")

    print("Testing connection to Contentful...")
    print(f"Space ID: {space_id}")
    print(f"Access Token: {access_token[:10]}...")

    try:
        # Create Contentful client
        client = contentful.Client(space_id, access_token)

        # Test connection by getting space info
        space = client.space()
        print(f"\n✅ Connected to space: {space.name}")
        print(f"Space ID: {space.sys['id']}")

        # List existing content types
        print("\n📋 Existing Content Types:")
        content_types = client.content_types()

        if content_types:
            for ct in content_types:
                print(f"  - {ct.name} (ID: {ct.sys['id']})")
                print(f"    Display Field: {getattr(ct, 'display_field', 'None')}")
                print(f"    Fields: {len(ct.fields)} fields")
                for field in ct.fields[:3]:  # Show first 3 fields
                    print(f"      • {field.name} ({field.type})")
                if len(ct.fields) > 3:
                    print(f"      ... and {len(ct.fields) - 3} more fields")
                print()
        else:
            print("  No content types found")

        # Get detailed field information for Article content type
        print("🔍 Detailed Article Content Type Analysis:")
        for ct in content_types:
            if ct.name == "Article":
                print("\nArticle Content Type Fields:")
                for field in ct.fields:
                    field_info = {
                        "id": field.id,
                        "name": field.name,
                        "type": field.type,
                        "required": getattr(field, "required", False),
                    }
                    print(f"  • {field.name}")
                    print(f"    ID: {field.id}")
                    print(f"    Type: {field.type}")
                    print(f"    Required: {getattr(field, 'required', False)}")

                    # Check for validation rules
                    if hasattr(field, "validations") and field.validations:
                        print(f"    Validations: {field.validations}")
                    print()

        # Try to get sample entries
        print("📄 Sample Entries:")
        try:
            entries = client.entries()
            if entries:
                for entry in entries[:3]:  # First 3 entries
                    content_type = getattr(entry, "content_type", None)
                    ct_name = content_type.name if content_type else "Unknown"
                    print(f"  - Entry ID: {entry.sys['id']} (Type: {ct_name})")
            else:
                print("  No entries found")
        except Exception as e:
            print(f"  Could not fetch entries: {e}")

    except Exception as e:
        print(f"❌ Error connecting to Contentful: {e}")
        return False

    return True


if __name__ == "__main__":
    test_contentful_connection()
