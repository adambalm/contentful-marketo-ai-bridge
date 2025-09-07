#!/usr/bin/env python3
"""
Inspect how to properly create ContentTypeField objects
"""

import os

from contentful_management import Client
from contentful_management.content_type_field import ContentTypeField
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def inspect_field_creation():
    """Understand the proper way to create ContentTypeField objects"""

    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")

    print("🔍 Inspecting ContentTypeField creation...")

    try:
        # Create Management API client
        client = Client(management_token)
        space = client.spaces().find(space_id)
        environment = space.environments().find("master")
        article_ct = environment.content_types().find("article")

        # Get an existing field to understand its structure
        existing_field = article_ct.fields[0]
        print("\n🔍 Existing Field Analysis:")
        print(f"Type: {type(existing_field)}")
        print(f"Raw data: {existing_field.raw}")
        print(f"to_json(): {existing_field.to_json()}")

        # Try different ways to create a ContentTypeField
        print("\n🧪 Testing ContentTypeField creation:")

        # Method 1: From raw dictionary (like existing fields)
        try:
            raw_field_data = {
                "id": "has_images",
                "name": "Has Images",
                "type": "Boolean",
                "required": False,
            }
            new_field1 = ContentTypeField(raw_field_data)
            print("✅ Method 1 (raw dict): Created field")
            print(f"   to_json(): {new_field1.to_json()}")
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")

        # Method 2: Initialize with empty and set attributes
        try:
            new_field2 = ContentTypeField()
            new_field2.id = "has_images"
            new_field2.name = "Has Images"
            new_field2.type = "Boolean"
            new_field2.required = False
            print("✅ Method 2 (set attributes): Created field")
            print(f"   to_json(): {new_field2.to_json()}")
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")

        # Method 3: Copy existing field and modify
        try:
            # Create a copy of existing field structure
            new_field_raw = existing_field.raw.copy()
            new_field_raw["id"] = "has_images"
            new_field_raw["name"] = "Has Images"
            new_field_raw["type"] = "Boolean"
            new_field_raw["required"] = False

            # Remove any attributes that don't apply to Boolean fields
            fields_to_remove = ["validations", "items", "linkType"]
            for field_name in fields_to_remove:
                if field_name in new_field_raw:
                    del new_field_raw[field_name]

            new_field3 = ContentTypeField(new_field_raw)
            print("✅ Method 3 (copy existing): Created field")
            print(f"   to_json(): {new_field3.to_json()}")
        except Exception as e:
            print(f"❌ Method 3 failed: {e}")

        # Method 4: Build minimal raw structure based on existing field
        try:
            minimal_raw = {
                "id": "has_images",
                "name": "Has Images",
                "type": "Boolean",
                "localized": False,
                "required": False,
                "disabled": False,
                "omitted": False,
            }
            new_field4 = ContentTypeField(minimal_raw)
            print("✅ Method 4 (minimal raw): Created field")
            print(f"   to_json(): {new_field4.to_json()}")
        except Exception as e:
            print(f"❌ Method 4 failed: {e}")

    except Exception as e:
        print(f"❌ Inspection failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    inspect_field_creation()
