#!/usr/bin/env python3
"""
Debug Contentful Management API SDK usage
"""

import os

from contentful_management import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def debug_management_api():
    """Debug the Management API SDK structure and methods"""

    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")

    print("🔍 Debugging Contentful Management API SDK...")

    try:
        # Create Management API client
        client = Client(management_token)

        # Get the space
        space = client.spaces().find(space_id)
        print(f"✅ Space: {space.name}")

        # Get the environment
        environment = space.environments().find("master")
        print("✅ Environment: master")

        # Get the Article content type
        article_ct = environment.content_types().find("article")
        print("✅ Article content type found")

        # Debug the structure
        print("\n🔍 Content Type Object Inspection:")
        print(f"Type: {type(article_ct)}")
        print(f"Attributes: {dir(article_ct)}")

        print("\n🔍 Fields Structure:")
        print(f"Fields type: {type(article_ct.fields)}")
        print(f"Fields length: {len(article_ct.fields)}")

        # Examine first field structure
        if article_ct.fields:
            first_field = article_ct.fields[0]
            print("\n🔍 First Field Structure:")
            print(f"Type: {type(first_field)}")
            print(f"Attributes: {dir(first_field)}")

        # Try different ways to add fields
        print("\n🔍 Environment Content Type Methods:")
        ct_methods = [
            method
            for method in dir(environment.content_types())
            if not method.startswith("_")
        ]
        print(f"Available methods: {ct_methods}")

        # Check if we can modify fields directly
        print("\n🔍 Trying to understand field modification...")

        # Create a new field definition
        new_field_def = {
            "id": "has_images",
            "name": "Has Images",
            "type": "Boolean",
            "required": False,
        }

        # Try different approaches to add the field
        print("\n🧪 Testing field addition approaches:")

        # Approach 1: Direct field manipulation
        try:
            current_fields = list(article_ct.fields)
            print(f"Current fields count: {len(current_fields)}")

            # Add new field to the list
            current_fields.append(new_field_def)
            article_ct.fields = current_fields

            print("✅ Approach 1: Direct field list manipulation - seems to work")
            print(f"New fields count: {len(article_ct.fields)}")

        except Exception as e:
            print(f"❌ Approach 1 failed: {e}")

        # Try to save (but don't actually save yet)
        print("\n🧪 Testing save operation:")
        try:
            # Show what would be saved
            print(f"Content type fields before save: {len(article_ct.fields)}")
            for field in article_ct.fields:
                if hasattr(field, "id"):
                    print(f"  - {field.name} ({field.id})")
                else:
                    print(f"  - {field}")
        except Exception as e:
            print(f"Error examining fields: {e}")

        # Don't actually save yet - just debug
        print("\n⚠️ Not saving changes yet - debug mode only")

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_management_api()
