#!/usr/bin/env python3
"""
Properly update Contentful Article content model using correct SDK methods
"""

import os

from contentful_management import Client
from contentful_management.content_type_field import ContentTypeField
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def fix_article_content_model():
    """Update the Article content model with proper field objects"""

    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")

    print("🔧 Fixing Article content model with proper SDK usage...")
    print(f"Space ID: {space_id}")

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
        for field in article_ct.fields:
            print(
                f"  • {field.name} (ID: {field.id}, Type: {field.type}, Required: {field.required})"
            )
            existing_field_ids.append(field.id)

        # Define the new fields we need to add
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

        # Create proper ContentTypeField objects and add them
        current_fields = list(article_ct.fields)  # Copy existing fields

        for field_data in fields_to_add:
            # Create a proper ContentTypeField object
            new_field = ContentTypeField(field_data)
            current_fields.append(new_field)
            print(f"  ✅ Prepared field: {field_data['name']}")

        # Update the content type with the new fields
        article_ct.fields = current_fields

        print("\n💾 Saving content type...")
        article_ct = article_ct.save()
        print("✅ Content type saved successfully")

        print("\n📡 Publishing content type...")
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
    success = fix_article_content_model()
    if success:
        print("\n✅ Content model update completed!")
        print("Next steps:")
        print("  1. Create sample articles with the new fields")
        print("  2. Test the live Contentful integration")
        print("  3. Update backend service to use real data")
    else:
        print("\n❌ Content model update failed - check errors above")
