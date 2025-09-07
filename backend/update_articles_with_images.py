#!/usr/bin/env python3
"""
Update existing Contentful articles with uploaded images.
Assigns professional marketing images to articles that need visual content.
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


def get_articles():
    """Get all articles from Contentful"""
    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    access_token = os.getenv("CONTENTFUL_ACCESS_TOKEN")

    if not space_id or not access_token:
        print("❌ Missing Contentful credentials")
        return []

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.contentful.delivery.v1+json",
    }

    response = requests.get(
        f"https://cdn.contentful.com/spaces/{space_id}/entries?content_type=article",
        headers=headers,
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("items", [])
    else:
        print(f"❌ Failed to fetch articles: {response.status_code}")
        return []


def get_assets():
    """Get all assets from Contentful"""
    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    access_token = os.getenv("CONTENTFUL_ACCESS_TOKEN")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.contentful.delivery.v1+json",
    }

    response = requests.get(
        f"https://cdn.contentful.com/spaces/{space_id}/assets", headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("items", [])
    else:
        print(f"❌ Failed to fetch assets: {response.status_code}")
        return []


def update_article_with_images(article_id, featured_image_id, gallery_image_ids=None):
    """Update an article with featured image and optional gallery"""
    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")

    headers = {
        "Authorization": f"Bearer {management_token}",
        "Content-Type": "application/vnd.contentful.management.v1+json",
    }

    # Get current article
    response = requests.get(
        f"https://api.contentful.com/spaces/{space_id}/entries/{article_id}",
        headers=headers,
    )

    if response.status_code != 200:
        print(f"❌ Failed to get article {article_id}: {response.status_code}")
        return False

    article = response.json()
    fields = article.get("fields", {})

    # Add featured image
    if featured_image_id:
        fields["featured_image"] = {
            "en-US": {
                "sys": {"type": "Link", "linkType": "Asset", "id": featured_image_id}
            }
        }

    # Add gallery images if provided
    if gallery_image_ids:
        fields["image_gallery"] = {
            "en-US": [
                {"sys": {"type": "Link", "linkType": "Asset", "id": img_id}}
                for img_id in gallery_image_ids
            ]
        }

    # Update article
    update_payload = {"fields": fields}

    update_response = requests.put(
        f"https://api.contentful.com/spaces/{space_id}/entries/{article_id}",
        headers={**headers, "X-Contentful-Version": str(article["sys"]["version"])},
        json=update_payload,
    )

    if update_response.status_code == 200:
        updated_article = update_response.json()

        # Publish the updated article
        publish_response = requests.put(
            f"https://api.contentful.com/spaces/{space_id}/entries/{article_id}/published",
            headers={
                "Authorization": f"Bearer {management_token}",
                "X-Contentful-Version": str(updated_article["sys"]["version"]),
            },
        )

        if publish_response.status_code == 200:
            return True
        else:
            print(
                f"❌ Failed to publish article {article_id}: {publish_response.status_code}"
            )
            return False
    else:
        print(
            f"❌ Failed to update article {article_id}: {update_response.status_code} - {update_response.text}"
        )
        return False


def main():
    """Main execution - assign images to articles intelligently"""
    print("🖼️  Updating Articles with Professional Images")
    print("=" * 50)

    # Get articles and assets
    print("📊 Fetching content...")
    articles = get_articles()
    assets = get_assets()

    if not articles:
        print("❌ No articles found")
        return False

    if not assets:
        print("❌ No assets found - run add_image_fields.py first")
        return False

    print(f"   • Found {len(articles)} articles")
    print(f"   • Found {len(assets)} assets")

    # Map assets by title/content for smart assignment
    marketing_images = []
    content_images = []
    analytics_images = []

    for asset in assets:
        title_field = asset.get("fields", {}).get("title", {})
        if isinstance(title_field, dict):
            title = title_field.get("en-US", "").lower()
        else:
            title = str(title_field).lower()
        if "marketing" in title or "automation" in title:
            marketing_images.append(asset["sys"]["id"])
        elif "content" in title or "strategy" in title:
            content_images.append(asset["sys"]["id"])
        elif "analytics" in title or "dashboard" in title:
            analytics_images.append(asset["sys"]["id"])

    print("\n🎯 Smart Image Assignment:")
    print(f"   • Marketing images: {len(marketing_images)}")
    print(f"   • Content images: {len(content_images)}")
    print(f"   • Analytics images: {len(analytics_images)}")

    updated_count = 0

    for article in articles:
        article_id = article["sys"]["id"]
        title_field = article.get("fields", {}).get("title", {})
        if isinstance(title_field, dict):
            title = title_field.get("en-US", "").lower()
        else:
            title = str(title_field).lower()

        # Check if article already has images
        has_featured = "featured_image" in article.get("fields", {})
        has_gallery = "image_gallery" in article.get("fields", {})

        if has_featured and has_gallery:
            print(f"   ⏭️  Skipping '{title}' - already has images")
            continue

        # Smart assignment based on article title/content
        featured_image_id = None
        gallery_ids = []

        if "marketing" in title or "automation" in title or "campaign" in title:
            if marketing_images:
                featured_image_id = marketing_images[0]
                gallery_ids = marketing_images[1:2] if len(marketing_images) > 1 else []
        elif "content" in title or "strategy" in title:
            if content_images:
                featured_image_id = content_images[0]
                gallery_ids = content_images[1:2] if len(content_images) > 1 else []
        elif "analytics" in title or "data" in title or "performance" in title:
            if analytics_images:
                featured_image_id = analytics_images[0]
                gallery_ids = analytics_images[1:2] if len(analytics_images) > 1 else []
        else:
            # Default assignment - use first available image
            if marketing_images:
                featured_image_id = marketing_images[0]
            elif content_images:
                featured_image_id = content_images[0]
            elif analytics_images:
                featured_image_id = analytics_images[0]

        if featured_image_id:
            print(f"   🔧 Updating '{title}'...")
            if update_article_with_images(article_id, featured_image_id, gallery_ids):
                updated_count += 1
                print("      ✅ Added images successfully")
            else:
                print("      ❌ Failed to update")
        else:
            print(f"   ⚠️  No suitable image for '{title}'")

    print("\n🎉 Update Complete!")
    print(f"   • Updated {updated_count}/{len(articles)} articles with images")
    print("   • Articles now have professional visual content")
    print("   • Ready for vision AI alt-text generation")

    return updated_count > 0


if __name__ == "__main__":
    main()
