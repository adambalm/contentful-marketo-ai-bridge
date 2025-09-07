#!/usr/bin/env python3
"""
Update Contentful Article content model to match our requirements
"""

import os

from contentful_management import Client
from contentful_management.errors import NotFoundError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def update_article_content_model():
    """Update the existing Article content model with required fields"""

    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")

    print("🔧 Updating Article content model...")
    print(f"Space ID: {space_id}")
    print(f"Management Token: {management_token[:10]}...")

    try:
        # Create Management API client
        client = Client(management_token)

        # Get the space
        space = client.spaces().find(space_id)
        print(f"✅ Connected to space: {space.name}")

        # Get the environment (usually 'master')
        environment = space.environments().find("master")
        print("✅ Using environment: master")

        # Get the existing Article content type
        try:
            article_ct = environment.content_types().find("article")
            print("✅ Found existing Article content type")
            print(f"Current fields: {len(article_ct.fields)}")

            # Show current fields
            print("\n📋 Current Article Fields:")
            for field in article_ct.fields:
                print(
                    f"  • {field.name} (ID: {field.id}, Type: {field.type}, Required: {getattr(field, 'required', False)})"
                )

        except NotFoundError:
            print("❌ Article content type not found")
            return False

        # Define the fields we need to add
        new_fields = [
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
        existing_field_ids = [field.id for field in article_ct.fields]
        print("\n🔍 Checking for missing fields...")

        fields_to_add = []
        for new_field in new_fields:
            if new_field["id"] not in existing_field_ids:
                fields_to_add.append(new_field)
                print(f"  ➕ Need to add: {new_field['name']}")
            else:
                print(f"  ✅ Already exists: {new_field['name']}")

        if fields_to_add:
            print(f"\n🔨 Adding {len(fields_to_add)} missing fields...")

            # Add the new fields using the Management API
            for field_data in fields_to_add:
                try:
                    # Create a new field object
                    new_field = environment.content_type_fields(article_ct.id).create(
                        field_data
                    )
                    print(f"  ✅ Added field: {field_data['name']}")
                except Exception as e:
                    print(f"  ❌ Failed to add field {field_data['name']}: {e}")

            # Refresh the content type to get updated fields
            article_ct = environment.content_types().find("article")

            # Publish the changes
            try:
                article_ct.publish()
                print("✅ Content type published")
            except Exception as e:
                print(f"⚠️ Could not publish automatically: {e}")
                print("Please publish manually in Contentful web interface")

        else:
            print("✅ All required fields already exist")

        # Also check if we need to make body field required
        body_field = next((f for f in article_ct.fields if f.id == "body"), None)
        if body_field and not getattr(body_field, "required", False):
            print("\n⚠️ Body field is optional but should be required")
            print(
                "Note: Making existing optional fields required needs careful consideration"
            )
            print("Recommendation: Update manually through Contentful web interface")

        print("\n📊 Final Article Content Type:")
        print(f"Total fields: {len(article_ct.fields)}")
        for field in article_ct.fields:
            print(
                f"  • {field.name} (ID: {field.id}, Type: {field.type}, Required: {getattr(field, 'required', False)})"
            )

        return True

    except Exception as e:
        print(f"❌ Error updating content model: {e}")
        return False


if __name__ == "__main__":
    success = update_article_content_model()
    if success:
        print("\n🎉 Content model update completed successfully!")
        print("Next steps:")
        print("  1. Verify fields in Contentful web interface")
        print("  2. Create sample content for testing")
        print("  3. Update backend service to use live API")
    else:
        print("\n❌ Content model update failed")
