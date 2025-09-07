#!/usr/bin/env python3
"""
Properly update Contentful Article content model - fixing defaultValue issue
"""

import os

from contentful_management import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def fix_article_content_model_v2():
    """Update the Article content model avoiding defaultValue None issues"""

    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")

    print("🔧 Fixing Article content model (v2 - avoiding defaultValue None)...")

    try:
        # Create Management API client
        client = Client(management_token)

        # Get the space and environment
        space = client.spaces().find(space_id)
        environment = space.environments().find("master")

        # Get the existing Article content type
        article_ct = environment.content_types().find("article")
        print(f"✅ Found Article content type with {len(article_ct.fields)} fields")

        # Show current fields
        print("\n📋 Current Fields:")
        existing_field_ids = []
        current_field_definitions = []

        for field in article_ct.fields:
            print(
                f"  • {field.name} (ID: {field.id}, Type: {field.type}, Required: {field.required})"
            )
            existing_field_ids.append(field.id)

            # Create clean field definition without None values
            field_def = {
                "id": field.id,
                "name": field.name,
                "type": field.type,
                "required": field.required,
            }

            # Only add non-None optional attributes
            if hasattr(field, "localized") and field.localized:
                field_def["localized"] = field.localized
            if hasattr(field, "disabled") and field.disabled:
                field_def["disabled"] = field.disabled
            if hasattr(field, "omitted") and field.omitted:
                field_def["omitted"] = field.omitted
            if hasattr(field, "validations") and field.validations:
                field_def["validations"] = field.validations
            if hasattr(field, "items") and field.items:
                field_def["items"] = field.items

            current_field_definitions.append(field_def)

        # Define the new fields we need to add (clean definitions)
        new_fields_data = [
            {
                "id": "has_images",
                "name": "Has Images",
                "type": "Boolean",
                "required": False,
            },
            {
                "id": "alt_text",
                "name": "Alt Text",
                "type": "Text",
                "required": False,
            },
            {
                "id": "cta_text",
                "name": "CTA Text",
                "type": "Symbol",
                "required": False,
            },
            {
                "id": "cta_url",
                "name": "CTA URL",
                "type": "Symbol",
                "required": False,
            },
        ]

        # Check which fields need to be added
        fields_to_add = []
        for field_data in new_fields_data:
            if field_data["id"] not in existing_field_ids:
                fields_to_add.append(field_data)
                print(f"  ➕ Need to add: {field_data['name']}")
            else:
                print(f"  ✅ Already exists: {field_data['name']}")

        if not fields_to_add:
            print("✅ All required fields already exist!")
            return True

        print(f"\n🔨 Adding {len(fields_to_add)} new fields...")

        # Combine existing and new field definitions
        all_field_definitions = current_field_definitions + fields_to_add

        # Update the content type fields directly with clean definitions
        article_ct.fields = all_field_definitions

        print("💾 Saving content type...")
        article_ct = article_ct.save()
        print("✅ Content type saved successfully")

        print("📡 Publishing content type...")
        article_ct.publish()
        print("✅ Content type published successfully")

        # Verify the final result
        article_ct = environment.content_types().find("article")  # Refresh
        print(f"\n📊 Final Article Content Type ({len(article_ct.fields)} fields):")
        for field in article_ct.fields:
            print(
                f"  • {field.name} (ID: {field.id}, Type: {field.type}, Required: {field.required})"
            )

        print(
            f"\n🎉 Successfully added {len(fields_to_add)} fields to Article content type!"
        )
        return True

    except Exception as e:
        print(f"❌ Error updating content model: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = fix_article_content_model_v2()
    if success:
        print("\n✅ Content model update completed!")
        print("Ready to:")
        print("  1. Create sample articles with all required fields")
        print("  2. Test live Contentful integration")
        print("  3. Switch backend from mock to real service")
    else:
        print("\n❌ Content model update failed - analyze error above")
