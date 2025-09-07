#!/usr/bin/env python3
"""
Use direct HTTP API to fix the defaultValue None issue with Contentful Management API
"""

import os

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def direct_api_fix():
    """Use direct HTTP API calls to add fields without SDK defaultValue bug"""

    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")

    base_url = f"https://api.contentful.com/spaces/{space_id}/environments/master"
    headers = {
        "Authorization": f"Bearer {management_token}",
        "Content-Type": "application/vnd.contentful.management.v1+json",
    }

    print("🔧 Using direct HTTP API to fix content model...")

    try:
        # 1. Get current content type
        response = requests.get(f"{base_url}/content_types/article", headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to get content type: {response.status_code}")
            print(response.text)
            return False

        content_type = response.json()
        print(f"✅ Retrieved content type with {len(content_type['fields'])} fields")

        # 2. Show current fields
        print("\n📋 Current fields:")
        existing_field_ids = []
        for field in content_type["fields"]:
            print(f"  • {field['name']} (ID: {field['id']}, Type: {field['type']})")
            existing_field_ids.append(field["id"])

        # 3. Define new fields to add (clean, without defaultValue)
        new_fields = [
            {
                "id": "has_images",
                "name": "Has Images",
                "type": "Boolean",
                "localized": False,
                "required": False,
                "disabled": False,
                "omitted": False,
                "validations": [],
            },
            {
                "id": "alt_text",
                "name": "Alt Text",
                "type": "Text",
                "localized": False,
                "required": False,
                "disabled": False,
                "omitted": False,
                "validations": [],
            },
            {
                "id": "cta_text",
                "name": "CTA Text",
                "type": "Symbol",
                "localized": False,
                "required": False,
                "disabled": False,
                "omitted": False,
                "validations": [],
            },
            {
                "id": "cta_url",
                "name": "CTA URL",
                "type": "Symbol",
                "localized": False,
                "required": False,
                "disabled": False,
                "omitted": False,
                "validations": [],
            },
        ]

        # 4. Filter to only new fields
        fields_to_add = [f for f in new_fields if f["id"] not in existing_field_ids]

        if not fields_to_add:
            print("✅ All fields already exist!")
            return True

        print(f"\n🔨 Adding {len(fields_to_add)} new fields...")
        for field in fields_to_add:
            print(f"  ➕ {field['name']}")

        # 5. Add new fields to existing fields list
        updated_content_type = content_type.copy()
        updated_content_type["fields"] = content_type["fields"] + fields_to_add

        # 6. Clean up the payload - remove sys and other metadata
        clean_payload = {
            "name": updated_content_type["name"],
            "description": updated_content_type.get("description", ""),
            "displayField": updated_content_type.get("displayField"),
            "fields": updated_content_type["fields"],
        }

        # 7. Send the update
        print("\n💾 Updating content type...")
        update_url = f"{base_url}/content_types/article"
        update_headers = headers.copy()
        update_headers["X-Contentful-Version"] = str(content_type["sys"]["version"])

        response = requests.put(update_url, headers=update_headers, json=clean_payload)

        if response.status_code == 200:
            print("✅ Content type updated successfully!")
            updated_ct = response.json()

            # 8. Publish the changes
            print("📡 Publishing content type...")
            publish_url = f"{base_url}/content_types/article/published"
            publish_headers = headers.copy()
            publish_headers["X-Contentful-Version"] = str(updated_ct["sys"]["version"])

            publish_response = requests.put(publish_url, headers=publish_headers)

            if publish_response.status_code == 200:
                print("✅ Content type published successfully!")

                # 9. Verify final result
                final_response = requests.get(
                    f"{base_url}/content_types/article", headers=headers
                )
                final_ct = final_response.json()

                print(f"\n📊 Final Content Type ({len(final_ct['fields'])} fields):")
                for field in final_ct["fields"]:
                    print(
                        f"  • {field['name']} (ID: {field['id']}, Type: {field['type']})"
                    )

                return True
            else:
                print(f"❌ Failed to publish: {publish_response.status_code}")
                print(publish_response.text)
                return False
        else:
            print(f"❌ Failed to update content type: {response.status_code}")
            print(response.text)
            return False

    except Exception as e:
        print(f"❌ Direct API call failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = direct_api_fix()
    if success:
        print("\n🎉 SUCCESS! SDK bug bypassed, content model updated!")
        print("Ready to test live Contentful integration")
    else:
        print("\n❌ Direct API approach also failed")
