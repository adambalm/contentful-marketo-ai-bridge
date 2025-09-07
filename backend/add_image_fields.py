#!/usr/bin/env python3
"""
Add proper Media fields to Article content type for professional image handling
"""

import os
import sys
from pathlib import Path

import requests

# Add parent directory to path for secure environment loading
sys.path.insert(0, str(Path(__file__).parent))
from load_env import load_environment

# Load environment variables securely
load_environment()


def add_image_fields():
    """Add Media fields to Article content type"""

    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")

    print("📸 Adding image fields to Article content type...")

    # Get current content type
    headers = {
        "Authorization": f"Bearer {management_token}",
        "Content-Type": "application/vnd.contentful.management.v1+json",
    }

    response = requests.get(
        f"https://api.contentful.com/spaces/{space_id}/content_types/article",
        headers=headers,
    )

    if response.status_code != 200:
        print(f"❌ Failed to get content type: {response.status_code}")
        return False

    content_type = response.json()
    current_fields = content_type["fields"]

    # Check if featured_image field already exists
    existing_field_ids = [field["id"] for field in current_fields]

    new_fields = []

    # Add featured image field (single Media)
    if "featured_image" not in existing_field_ids:
        new_fields.append(
            {
                "id": "featured_image",
                "name": "Featured Image",
                "type": "Link",
                "linkType": "Asset",
                "required": False,
                "disabled": False,
                "omitted": False,
                "validations": [{"linkMimetypeGroup": ["image"]}],
            }
        )

    # Add gallery field (multiple Media)
    if "image_gallery" not in existing_field_ids:
        new_fields.append(
            {
                "id": "image_gallery",
                "name": "Image Gallery",
                "type": "Array",
                "required": False,
                "disabled": False,
                "omitted": False,
                "items": {
                    "type": "Link",
                    "linkType": "Asset",
                    "validations": [{"linkMimetypeGroup": ["image"]}],
                },
                "validations": [{"size": {"max": 10}}],
            }
        )

    if not new_fields:
        print("✅ Image fields already exist")
        return True

    # Add new fields to existing fields
    updated_fields = current_fields + new_fields

    # Update content type
    update_payload = {
        "name": content_type["name"],
        "description": content_type.get("description", ""),
        "fields": updated_fields,
    }

    # Remove system fields that can't be updated
    clean_payload = {}
    for key, value in update_payload.items():
        if key not in ["sys", "metadata"]:
            clean_payload[key] = value

    print(f"🔧 Adding {len(new_fields)} new image fields...")

    # Update the content type
    update_response = requests.put(
        f"https://api.contentful.com/spaces/{space_id}/content_types/article",
        headers={
            "Authorization": f"Bearer {management_token}",
            "Content-Type": "application/vnd.contentful.management.v1+json",
            "X-Contentful-Version": str(content_type["sys"]["version"]),
        },
        json=clean_payload,
    )

    if update_response.status_code == 200:
        updated_type = update_response.json()
        print("✅ Content type updated successfully")

        # Publish the content type
        publish_response = requests.put(
            f"https://api.contentful.com/spaces/{space_id}/content_types/article/published",
            headers={
                "Authorization": f"Bearer {management_token}",
                "X-Contentful-Version": str(updated_type["sys"]["version"]),
            },
        )

        if publish_response.status_code == 200:
            print("✅ Content type published successfully")

            # Show final field list
            final_fields = updated_type["fields"]
            print(f"\n📋 Final Article fields ({len(final_fields)} total):")
            for field in final_fields:
                field_type = field["type"]
                if field_type == "Array" and "items" in field:
                    field_type = f"Array of {field['items']['type']}"
                elif field_type == "Link" and "linkType" in field:
                    field_type = f"Link to {field['linkType']}"
                print(f"  • {field['id']}: {field_type} (\"{field['name']}\")")

            return True
        else:
            print(
                f"❌ Failed to publish: {publish_response.status_code} - {publish_response.text}"
            )
            return False
    else:
        print(
            f"❌ Failed to update: {update_response.status_code} - {update_response.text}"
        )
        return False


def upload_sample_image():
    """Upload a sample marketing image to use in articles"""

    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")

    print("\n🖼️  Uploading sample marketing images...")

    # Create sample images using Python
    try:
        import base64
        import io

        from PIL import Image, ImageDraw, ImageFont

        def create_marketing_image(title, subtitle, color, size=(800, 400)):
            """Create a professional marketing image"""
            img = Image.new("RGB", size, color=color)
            draw = ImageDraw.Draw(img)

            try:
                # Try to use system font
                title_font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36
                )
                subtitle_font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24
                )
            except:
                # Fallback to default font
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()

            # Calculate text positions (centered)
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]

            subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]

            # Draw text
            title_x = (size[0] - title_width) // 2
            title_y = (size[1] - title_height - subtitle_height - 20) // 2

            subtitle_x = (size[0] - subtitle_width) // 2
            subtitle_y = title_y + title_height + 20

            draw.text((title_x, title_y), title, fill="white", font=title_font)
            draw.text(
                (subtitle_x, subtitle_y), subtitle, fill="white", font=subtitle_font
            )

            return img

        # Create sample images
        images_to_create = [
            {
                "title": "Marketing Automation",
                "subtitle": "Streamline Your Campaigns",
                "color": "#0066cc",
                "filename": "marketing-automation-hero.png",
                "description": "Professional marketing automation hero image with blue corporate branding",
            },
            {
                "title": "Content Strategy",
                "subtitle": "Build Engaging Experiences",
                "color": "#28a745",
                "filename": "content-strategy-guide.png",
                "description": "Content strategy guide with green professional color scheme",
            },
            {
                "title": "Analytics Dashboard",
                "subtitle": "Data-Driven Decisions",
                "color": "#dc3545",
                "filename": "analytics-dashboard-preview.png",
                "description": "Analytics dashboard preview with red accent highlighting performance metrics",
            },
        ]

        uploaded_assets = []

        for image_config in images_to_create:
            print(f"   Creating: {image_config['filename']}")

            # Create the image
            img = create_marketing_image(
                image_config["title"], image_config["subtitle"], image_config["color"]
            )

            # Convert to bytes
            img_byte_array = io.BytesIO()
            img.save(img_byte_array, format="PNG")
            img_bytes = img_byte_array.getvalue()

            # Upload to Contentful
            upload_headers = {
                "Authorization": f"Bearer {management_token}",
                "Content-Type": "application/octet-stream",
            }

            # Step 1: Upload binary data
            upload_response = requests.post(
                f"https://upload.contentful.com/spaces/{space_id}/uploads",
                headers=upload_headers,
                data=img_bytes,
            )

            if upload_response.status_code == 201:
                upload_data = upload_response.json()
                upload_id = upload_data["sys"]["id"]

                # Step 2: Create asset from upload
                asset_payload = {
                    "fields": {
                        "title": {"en-US": image_config["title"]},
                        "description": {"en-US": image_config["description"]},
                        "file": {
                            "en-US": {
                                "contentType": "image/png",
                                "fileName": image_config["filename"],
                                "uploadFrom": {
                                    "sys": {
                                        "type": "Link",
                                        "linkType": "Upload",
                                        "id": upload_id,
                                    }
                                },
                            }
                        },
                    }
                }

                asset_response = requests.post(
                    f"https://api.contentful.com/spaces/{space_id}/assets",
                    headers={
                        "Authorization": f"Bearer {management_token}",
                        "Content-Type": "application/vnd.contentful.management.v1+json",
                    },
                    json=asset_payload,
                )

                if asset_response.status_code == 201:
                    asset = asset_response.json()
                    asset_id = asset["sys"]["id"]

                    # Step 3: Process asset
                    process_response = requests.put(
                        f"https://api.contentful.com/spaces/{space_id}/assets/{asset_id}/files/en-US/process",
                        headers={
                            "Authorization": f"Bearer {management_token}",
                            "X-Contentful-Version": str(asset["sys"]["version"]),
                        },
                    )

                    if process_response.status_code in [200, 204]:
                        # Step 4: Publish asset
                        # Get updated asset
                        get_response = requests.get(
                            f"https://api.contentful.com/spaces/{space_id}/assets/{asset_id}",
                            headers={"Authorization": f"Bearer {management_token}"},
                        )

                        if get_response.status_code == 200:
                            updated_asset = get_response.json()

                            publish_response = requests.put(
                                f"https://api.contentful.com/spaces/{space_id}/assets/{asset_id}/published",
                                headers={
                                    "Authorization": f"Bearer {management_token}",
                                    "X-Contentful-Version": str(
                                        updated_asset["sys"]["version"]
                                    ),
                                },
                            )

                            if publish_response.status_code == 200:
                                published_asset = publish_response.json()
                                file_url = published_asset["fields"]["file"]["en-US"][
                                    "url"
                                ]
                                print(f"     ✅ Uploaded: https:{file_url}")

                                uploaded_assets.append(
                                    {
                                        "id": asset_id,
                                        "title": image_config["title"],
                                        "filename": image_config["filename"],
                                        "url": f"https:{file_url}",
                                    }
                                )
                            else:
                                print(
                                    f"     ❌ Failed to publish asset: {publish_response.status_code}"
                                )
                        else:
                            print(
                                f"     ❌ Failed to get updated asset: {get_response.status_code}"
                            )
                    else:
                        print(
                            f"     ❌ Failed to process asset: {process_response.status_code}"
                        )
                else:
                    print(
                        f"     ❌ Failed to create asset: {asset_response.status_code} - {asset_response.text}"
                    )
            else:
                print(
                    f"     ❌ Failed to upload: {upload_response.status_code} - {upload_response.text}"
                )

        print(f"\n✅ Uploaded {len(uploaded_assets)} images to Contentful")
        return uploaded_assets

    except ImportError:
        print("❌ Pillow not available - cannot create sample images")
        print("   Install with: pip install Pillow")
        return []
    except Exception as e:
        print(f"❌ Error creating images: {e}")
        return []


def main():
    """Main execution"""
    print("🎨 Professional Image Integration Setup")
    print("=" * 50)

    # Step 1: Add image fields to content model
    if add_image_fields():
        # Step 2: Upload sample images
        uploaded_assets = upload_sample_image()

        if uploaded_assets:
            print("\n🎉 Setup complete!")
            print("   • Added image fields to Article content type")
            print(f"   • Uploaded {len(uploaded_assets)} professional sample images")
            print("   • Ready to add images to articles")

            print("\n📋 Next Steps:")
            print("   1. Edit articles in Contentful to add featured images")
            print("   2. Test vision AI alt-text generation with real images")
            print("   3. Verify professional appearance in content activation")

            return True
        else:
            print("\n⚠️  Content model updated but no images uploaded")
            print("   Add images manually in Contentful web interface")

    return False


if __name__ == "__main__":
    main()
