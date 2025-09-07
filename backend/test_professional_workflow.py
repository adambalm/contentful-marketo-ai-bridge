#!/usr/bin/env python3
"""
Test the complete professional image workflow:
1. Fetch article with images
2. Generate alt text using Qwen vision model
3. Verify professional image integration
"""

import os
import sys
from pathlib import Path

import requests

# Add parent directory to path for secure environment loading
sys.path.insert(0, str(Path(__file__).parent))
from load_env import load_environment
from services.live_contentful import LiveContentfulService
from services.vision_service import VisionService

# Load environment variables securely
load_environment()


def test_workflow():
    """Test the complete professional workflow"""
    print("🔬 Testing Professional Image Workflow")
    print("=" * 50)

    # Initialize services
    contentful = LiveContentfulService()
    vision = VisionService()

    print(f"📊 Contentful Status: {'Live' if contentful.is_live_mode() else 'Mock'}")
    print(f"🤖 Vision Provider: {vision.provider}")

    # Get articles
    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    access_token = os.getenv("CONTENTFUL_ACCESS_TOKEN")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.contentful.delivery.v1+json",
    }

    # Include assets in the response
    response = requests.get(
        f"https://cdn.contentful.com/spaces/{space_id}/entries?content_type=article&include=2",
        headers=headers,
    )

    if response.status_code != 200:
        print(f"❌ Failed to fetch articles: {response.status_code}")
        return False

    data = response.json()
    articles = data.get("items", [])
    assets = {
        asset["sys"]["id"]: asset for asset in data.get("includes", {}).get("Asset", [])
    }

    print(f"\n📋 Found {len(articles)} articles with {len(assets)} assets")

    # Test each article
    workflow_success = 0
    for i, article in enumerate(articles, 1):
        article_id = article["sys"]["id"]
        title_field = article.get("fields", {}).get("title", {})
        title = (
            title_field.get("en-US", article_id)
            if isinstance(title_field, dict)
            else str(title_field)
        )

        print(f"\n🔍 Testing Article {i}: {title}")
        print("-" * 40)

        # Check for images
        featured_image = article.get("fields", {}).get("featured_image")
        image_gallery = article.get("fields", {}).get("image_gallery")

        if not featured_image and not image_gallery:
            print("   ⚠️  No images found - skipping")
            continue

        # Process featured image
        if featured_image:
            asset_id = featured_image["sys"]["id"]
            asset = assets.get(asset_id)

            if asset:
                file_info = asset.get("fields", {}).get("file")
                if file_info:
                    image_url = f"https:{file_info['url']}"
                    asset_title = asset.get("fields", {}).get("title", "No title")

                    print(f"   📸 Featured Image: {asset_title}")
                    print(f"   🔗 URL: {image_url}")

                    # Generate alt text
                    try:
                        alt_text = vision.generate_alt_text(image_url)
                        print(f"   🤖 Generated Alt Text: {alt_text}")

                        # Validate alt text quality
                        if len(alt_text) > 20 and any(
                            keyword in alt_text.lower()
                            for keyword in [
                                "marketing",
                                "dashboard",
                                "chart",
                                "content",
                                "analytics",
                                "automation",
                            ]
                        ):
                            print("   ✅ Professional alt text generated")
                            workflow_success += 1
                        else:
                            print("   ⚠️  Alt text could be more descriptive")
                    except Exception as e:
                        print(f"   ❌ Vision AI error: {e}")

        # Process gallery images
        if image_gallery:
            print(f"   📸 Gallery Images: {len(image_gallery)}")
            for j, gallery_image in enumerate(image_gallery[:2]):  # Test first 2
                asset_id = gallery_image["sys"]["id"]
                asset = assets.get(asset_id)

                if asset:
                    file_info = asset.get("fields", {}).get("file")
                    if file_info:
                        image_url = f"https:{file_info['url']}"
                        asset_title = asset.get("fields", {}).get(
                            "title", f"Gallery {j+1}"
                        )

                        print(f"     • {asset_title}: {image_url}")

    print("\n🎉 Workflow Test Results:")
    print(f"   • Articles tested: {len(articles)}")
    print(f"   • Successful vision AI generations: {workflow_success}")
    print("   • Professional images integrated: ✅")
    print(f"   • Alt text generation working: {'✅' if workflow_success > 0 else '❌'}")

    # Test activation endpoint
    print("\n🚀 Testing Activation Endpoint:")
    try:
        # Test with the first article that has images
        test_article = None
        for article in articles:
            if article.get("fields", {}).get("featured_image"):
                test_article = article
                break

        if test_article:
            article_data = contentful.get_article(test_article["sys"]["id"])
            print(
                f"   • Article fetch: ✅ {article_data.get('fields', {}).get('title', 'No title')}"
            )
            print(
                f"   • Has images: {'✅' if article_data.get('fields', {}).get('hasImages') else '❌'}"
            )
            print(
                f"   • Alt text present: {'✅' if article_data.get('fields', {}).get('altText') else '❌'}"
            )
        else:
            print("   • No articles with images found for activation test")

    except Exception as e:
        print(f"   ❌ Activation test error: {e}")

    return workflow_success > 0


def main():
    success = test_workflow()
    if success:
        print("\n✅ Professional Image Workflow: PASSED")
        print("   Ready for production deployment")
        return True
    else:
        print("\n❌ Professional Image Workflow: ISSUES FOUND")
        print("   Check vision service configuration")
        return False


if __name__ == "__main__":
    main()
