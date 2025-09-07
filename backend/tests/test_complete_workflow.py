#!/usr/bin/env python3
"""
Test complete vision integration with actual Contentful data and local images.
"""

import base64
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from load_env import load_environment
from services.ai_service import AIService

# Load environment
load_environment()


def test_local_image_processing():
    """Test vision processing with local test images"""

    print("🎯 Complete Vision Integration Test")
    print("=" * 50)

    # Test data with embedded base64 images
    test_images = [
        "marketing_dashboard.png",
        "content_strategy.png",
        "analytics_chart.png",
    ]

    for image_file in test_images:
        if not Path(image_file).exists():
            print(f"❌ Missing test image: {image_file}")
            continue

        print(f"\n📊 Testing {image_file}")
        print("-" * 30)

        # Read image as base64
        with open(image_file, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("ascii")

        # Create article data with data URL
        data_url = f"data:image/png;base64,{image_data}"

        article_data = {
            "title": f"Marketing Analytics Report - {image_file}",
            "body": f"""
# Marketing Performance Dashboard

Our latest campaign results are shown in the dashboard below:

<img src="{data_url}" alt="" />

The metrics demonstrate significant improvement in our automation strategy.
            """,
            "has_images": True,
            "campaign_tags": ["marketing-automation", "analytics", "dashboard"],
        }

        # Test with AI service (uses AI_PROVIDER from environment - should be "local")
        ai_service = AIService()

        try:
            # Test URL extraction first
            from services.ai_service import LocalModelProvider

            provider = LocalModelProvider()
            urls = provider._extract_image_urls_from_content(article_data["body"])
            print(f"📍 Extracted URLs: {len(urls)} found")
            if urls:
                print(f"   First URL: {urls[0][:80]}...")

            # Test enrichment
            enrichment = ai_service.enrich_content(article_data)
            print(f"✅ Enrichment: {enrichment.suggested_meta_description[:50]}...")

            # Test alt text generation
            alt_text = ai_service.generate_alt_text(article_data)
            print(f"📝 Alt Text: {alt_text}")

            if (
                alt_text
                and alt_text != "Image description unavailable"
                and alt_text is not None
            ):
                print("🎉 Vision integration working!")
            else:
                print("⚠️ Vision integration needs debugging")

        except Exception as e:
            print(f"❌ Error: {e}")


def test_with_contentful_urls():
    """Test with Contentful asset URLs (if available)"""

    print("\n🔗 Testing Contentful Asset URLs")
    print("=" * 40)

    # Example Contentful asset URLs from our space
    contentful_article = {
        "title": "Contentful Marketing Asset Test",
        "body": """
# Visual Marketing Content

Check out our campaign dashboard:

![Marketing Dashboard](https://images.ctfassets.net/ebgprhvsyuge/sample-image-id/sample-file-id/dashboard.png)

This shows our latest performance metrics.
        """,
        "has_images": True,
        "campaign_tags": ["contentful", "cms", "marketing"],
    }

    ai_service = AIService()

    try:
        # Test URL extraction
        from services.ai_service import LocalModelProvider

        provider = LocalModelProvider()

        urls = provider._extract_image_urls_from_content(contentful_article["body"])
        print(f"📍 Extracted URLs: {urls}")

        if urls:
            alt_text = ai_service.generate_alt_text(contentful_article)
            print(f"📝 Alt Text: {alt_text}")
        else:
            print("ℹ️ No valid image URLs found")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_local_image_processing()
    test_with_contentful_urls()

    print("\n🚀 Integration test complete!")
    print("\nNext steps:")
    print("1. Add HTTP image download support to Qwen provider")
    print("2. Test with live Contentful articles containing images")
    print("3. Verify surrogate validation prevents corruption")
