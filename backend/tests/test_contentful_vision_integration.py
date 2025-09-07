#!/usr/bin/env python3
"""
Test updated vision processing with real Contentful Asset fields.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from load_env import load_environment
from services.ai_service import AIService
from services.live_contentful import LiveContentfulService

load_environment()


def test_contentful_asset_extraction():
    """Test that we can extract URLs from Contentful Asset objects"""

    print("🎯 Testing Contentful Asset Extraction & Vision Processing")
    print("=" * 60)

    contentful_service = LiveContentfulService()
    ai_service = AIService()

    if not contentful_service.live_mode:
        print("❌ Contentful not in live mode")
        return

    # Get live entries with Asset objects
    entries = contentful_service.client.entries()

    for i, entry in enumerate(entries[:2]):  # Test first 2 articles
        print(f"\n📄 Article {i+1}: {entry.title}")
        print("-" * 50)

        # Convert entry to format that includes Asset objects
        article_data = {
            "title": entry.title,
            "body": getattr(entry, "body", ""),
            "campaign_tags": getattr(entry, "campaign_tags", []) or ["contentful"],
            "has_images": bool(getattr(entry, "has_images", False)),
            "featured_image": getattr(entry, "featured_image", None),  # Asset object
            "image_gallery": getattr(
                entry, "image_gallery", []
            ),  # Array of Asset objects
            "alt_text": getattr(entry, "alt_text", None),
        }

        print(f"   Has Images: {article_data['has_images']}")
        print(f"   Featured Image: {type(article_data['featured_image'])}")
        if article_data["featured_image"]:
            print(f"      URL: {article_data['featured_image'].url}")
        print(f"   Image Gallery: {len(article_data.get('image_gallery', []))} items")

        # Test URL extraction from both sources
        from services.ai_service import LocalModelProvider

        provider = LocalModelProvider()

        # Test body URL extraction
        body_urls = provider._extract_image_urls_from_content(article_data["body"])
        print(f"   📝 Body URLs found: {len(body_urls)}")

        # Test Asset URL extraction
        asset_urls = provider._extract_contentful_asset_urls(article_data)
        print(f"   🖼️  Asset URLs found: {len(asset_urls)}")
        for j, url in enumerate(asset_urls):
            print(f"      {j+1}: {url}")

        # Test complete vision processing
        if article_data["has_images"]:
            print("\n   🎯 Testing Vision Processing...")
            try:
                alt_text = ai_service.generate_alt_text(article_data)
                if alt_text and alt_text != "Image description unavailable":
                    print(f"   ✅ Generated Alt Text: {alt_text}")
                elif alt_text == "Remote images not yet supported in local model":
                    print(f"   ⚠️  Qwen limitation: {alt_text}")
                elif alt_text is None:
                    print("   ❌ No alt text generated (no images found)")
                else:
                    print(f"   ❌ Failed: {alt_text}")
            except Exception as e:
                print(f"   ❌ Vision error: {e}")
        else:
            print("   ℹ️  Skipping vision (has_images=False)")


if __name__ == "__main__":
    test_contentful_asset_extraction()

    print("\n🏁 Asset Extraction Test Complete!")

    print("\n📋 Key Findings:")
    print("1. Articles have Asset objects in featured_image and image_gallery fields")
    print("2. Asset URLs are available via .url attribute")
    print("3. Vision processing should now find these Asset URLs")
    print("4. Need to verify Qwen can process HTTP URLs or add download capability")

    print("\n🔧 Remaining UX Questions:")
    print("- How to handle multiple images (featured + gallery)?")
    print("- Should we generate alt text for all images or just featured?")
    print("- How should users see/edit the generated alt text?")
    print("- Where should alt text be stored (single field vs per-image)?")
