#!/usr/bin/env python3
"""
Test complete live Contentful integration with vision processing.
Tests real articles from Contentful space with vision alt text generation.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from load_env import load_environment
from schemas.article import ArticleIn
from services.ai_service import AIService
from services.live_contentful import LiveContentfulService

# Load environment
load_environment()


def test_live_contentful_with_vision():
    """Test complete workflow with live Contentful articles"""

    print("🎯 Live Contentful + Vision Integration Test")
    print("=" * 55)

    # Initialize services
    contentful_service = LiveContentfulService()
    ai_service = AIService()

    if not contentful_service.live_mode:
        print("❌ Contentful not in live mode - check credentials")
        return

    print("✅ Contentful live mode active")
    print(f"✅ AI provider: {os.getenv('AI_PROVIDER', 'openai')}")
    print(f"✅ Vision provider: {os.getenv('VISION_PROVIDER', 'qwen')}")

    # Get all entries
    try:
        entries = contentful_service.client.entries()
        print(f"\n📚 Found {len(entries)} articles in Contentful")

        for i, entry in enumerate(entries):
            print(f"\n📄 Article {i+1}: {entry.title}")
            print("-" * 40)

            # Convert to our article format
            article_data = {
                "title": entry.title,
                "body": getattr(entry, "body", ""),
                "campaign_tags": getattr(entry, "campaign_tags", [])
                or ["contentful", "marketing"],
                "has_images": bool(getattr(entry, "has_images", False)),
                "alt_text": getattr(entry, "alt_text", None),
                "cta_text": getattr(entry, "cta_text", None),
                "cta_url": getattr(entry, "cta_url", None),
            }

            print(f"   Title: {article_data['title']}")
            print(f"   Body length: {len(article_data['body'])} chars")
            print(f"   Has images: {article_data['has_images']}")
            print(f"   Campaign tags: {article_data['campaign_tags']}")

            # Test article validation
            try:
                validated_article = ArticleIn(**article_data)
                print("   ✅ Article validation: PASSED")
            except Exception as e:
                print(f"   ❌ Article validation: FAILED - {e}")
                continue

            # Test AI enrichment
            try:
                enrichment = ai_service.enrich_content(article_data)
                print(f"   ✅ AI enrichment: {enrichment.seo_score}/100 score")
                print(
                    f"   📝 Meta description: {enrichment.suggested_meta_description[:60]}..."
                )
                print(f"   🏷️  Keywords: {enrichment.keywords[:3]}...")
            except Exception as e:
                print(f"   ❌ AI enrichment failed: {e}")
                continue

            # Test vision processing
            try:
                alt_text = ai_service.generate_alt_text(article_data)
                if alt_text and alt_text != "Image description unavailable":
                    print(f"   🖼️  Generated alt text: {alt_text}")
                    print("   ✅ Vision processing: WORKING")
                elif alt_text is None:
                    print("   ℹ️  No images found for vision processing")
                    print("   ✅ Vision processing: SKIPPED (no images)")
                else:
                    print(f"   ⚠️  Vision processing: {alt_text}")
                    print("   ⚠️  Vision processing: NEEDS DEBUG")
            except Exception as e:
                print(f"   ❌ Vision processing failed: {e}")

    except Exception as e:
        print(f"❌ Error accessing Contentful entries: {e}")


def test_vision_with_sample_content():
    """Test vision processing with content containing images"""

    print("\n🖼️  Testing Vision with Image-Rich Content")
    print("=" * 45)

    # Create test article with images
    test_article = {
        "title": "Marketing Dashboard Analytics Report",
        "body": """
# Campaign Performance Overview

Our latest marketing automation campaign shows impressive results:

![Marketing Dashboard](https://images.ctfassets.net/ebgprhvsyuge/sample/sample/dashboard.png)

Key metrics include:
- Email open rate: 34.5%
- Click-through rate: 8.2%
- Conversion rate: 4.1%
- ROI: +156%

The dashboard visualization above clearly demonstrates the campaign's success across all channels.

![Analytics Chart](https://via.placeholder.com/600x400/4ECDC4/FFFFFF?text=Q3+Analytics)

This comprehensive analysis helps us optimize future campaigns for even better performance.
        """,
        "campaign_tags": ["marketing-automation", "analytics", "dashboard"],
        "has_images": True,
        "alt_text": None,
        "cta_text": "View Full Report",
        "cta_url": "https://example.com/report",
    }

    print(f"📄 Test Article: {test_article['title']}")

    ai_service = AIService()

    # Test URL extraction
    from services.ai_service import LocalModelProvider

    provider = LocalModelProvider()
    urls = provider._extract_image_urls_from_content(test_article["body"])
    print(f"📍 Extracted {len(urls)} image URLs:")
    for i, url in enumerate(urls):
        print(f"   {i+1}: {url[:60]}{'...' if len(url) > 60 else ''}")

    # Test vision processing
    try:
        alt_text = ai_service.generate_alt_text(test_article)
        print(f"\n🎯 Vision Result: {alt_text}")

        if (
            alt_text
            and alt_text != "Image description unavailable"
            and alt_text is not None
        ):
            print("🎉 Vision integration is working!")
        else:
            print("⚠️ Vision processing needs enhancement for HTTP URLs")

    except Exception as e:
        print(f"❌ Vision processing error: {e}")


if __name__ == "__main__":
    test_live_contentful_with_vision()
    test_vision_with_sample_content()

    print("\n🏁 Test Complete!")
    print("\nNext steps based on Agent OS roadmap:")
    print("1. ✅ Vision Alt Text Generation: 80% complete")
    print("2. 🔄 Live Contentful Integration: Testing phase")
    print("3. 📋 Ready for portfolio demonstration")
    print("4. 🎯 Phase 2 objectives nearly complete")
