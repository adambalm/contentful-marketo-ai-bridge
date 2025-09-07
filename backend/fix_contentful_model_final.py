#!/usr/bin/env python3
"""
Final fix for Contentful Article content model - handling defaultValue correctly
"""

import os

from contentful_management import Client
from contentful_management.content_type_field import ContentTypeField
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def fix_article_content_model_final():
    """Update Article content model with proper defaultValue handling"""

    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")

    print("🔧 Final fix for Article content model...")

    try:
        # Create Management API client
        client = Client(management_token)
        space = client.spaces().find(space_id)
        environment = space.environments().find("master")
        article_ct = environment.content_types().find("article")

        print(f"✅ Found Article content type with {len(article_ct.fields)} fields")

        # Get existing field IDs
        existing_field_ids = [field.id for field in article_ct.fields]
        print(f"\n📋 Existing fields: {existing_field_ids}")

        # Define new fields with proper defaultValue for each type
        new_fields_specs = [
            {
                "id": "has_images",
                "name": "Has Images",
                "type": "Boolean",
                "required": False,
                "defaultValue": False,  # Proper Boolean default
            },
            {
                "id": "alt_text",
                "name": "Alt Text",
                "type": "Text",
                "required": False,
                # Text fields can omit defaultValue
            },
            {
                "id": "cta_text",
                "name": "CTA Text",
                "type": "Symbol",
                "required": False,
                # Symbol fields can omit defaultValue
            },
            {
                "id": "cta_url",
                "name": "CTA URL",
                "type": "Symbol",
                "required": False,
                # Symbol fields can omit defaultValue
            },
        ]

        # Filter to only fields we need to add
        fields_to_add = []
        for spec in new_fields_specs:
            if spec["id"] not in existing_field_ids:
                fields_to_add.append(spec)
                print(f"  ➕ Will add: {spec['name']}")
            else:
                print(f"  ✅ Exists: {spec['name']}")

        if not fields_to_add:
            print("✅ All required fields already exist!")
            return True

        print(f"\n🔨 Adding {len(fields_to_add)} fields...")

        # Create new ContentTypeField objects properly
        current_fields = list(article_ct.fields)  # Keep existing fields

        for spec in fields_to_add:
            # Build field data without None defaultValue where inappropriate
            field_data = {
                "id": spec["id"],
                "name": spec["name"],
                "type": spec["type"],
                "localized": False,
                "required": spec["required"],
                "disabled": False,
                "omitted": False,
                "validations": [],
            }

            # Only add defaultValue if we have a proper value
            if "defaultValue" in spec:
                field_data["defaultValue"] = spec["defaultValue"]

            # Create the field
            new_field = ContentTypeField(field_data)
            current_fields.append(new_field)
            print(f"  ✅ Created field: {spec['name']}")

            # Debug: show what will be sent
            field_json = new_field.to_json()
            print(f"    Field JSON: {field_json}")

        # Update content type
        article_ct.fields = current_fields

        print("\n💾 Saving content type...")
        try:
            article_ct = article_ct.save()
            print("✅ Content type saved")
        except Exception as save_error:
            print(f"❌ Save failed: {save_error}")
            # Let's see what we're trying to send
            print("\n🔍 Debug - content type data being sent:")
            try:
                ct_json = article_ct.to_json()
                print(f"Fields in JSON: {len(ct_json.get('fields', []))}")
                for i, field in enumerate(ct_json.get("fields", [])):
                    print(
                        f"  {i}: {field.get('name')} - defaultValue: {field.get('defaultValue')}"
                    )
            except Exception as debug_error:
                print(f"Debug failed: {debug_error}")
            raise save_error

        print("📡 Publishing content type...")
        article_ct.publish()
        print("✅ Published successfully")

        # Verify final result
        article_ct = environment.content_types().find("article")
        print(f"\n📊 Final Article Content Type ({len(article_ct.fields)} fields):")
        for field in article_ct.fields:
            print(f"  • {field.name} (ID: {field.id}, Type: {field.type})")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = fix_article_content_model_final()
    if success:
        print("\n🎉 SUCCESS! Content model is ready for integration")
    else:
        print("\n💡 If this still fails, we may need to use HTTP API directly")
