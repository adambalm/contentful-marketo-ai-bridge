#!/usr/bin/env python3
"""
Test script for vision-based alt text generation
Tests both GPT-4o and Qwen 2.5VL 7b providers
"""

import json
import os
import sys

from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import AIService
from services.vision_service import VisionService

load_dotenv()


def test_sample_images():
    """Test vision models with sample image URLs"""

    # Sample image URLs for testing (publicly accessible)
    test_images = [
        {
            "url": "https://via.placeholder.com/600x400/0066CC/FFFFFF?text=Marketing+Dashboard",
            "context": "marketing automation dashboard showing campaign performance metrics",
            "description": "A blue marketing dashboard placeholder image",
        },
        {
            "url": "https://via.placeholder.com/800x600/FF6B6B/FFFFFF?text=Content+Strategy",
            "context": "content strategy planning and workflow optimization",
            "description": "A red content strategy placeholder image",
        },
        {
            "url": "https://via.placeholder.com/400x300/4ECDC4/FFFFFF?text=Analytics",
            "context": "data analytics and performance tracking for marketing campaigns",
            "description": "A teal analytics placeholder image",
        },
    ]

    print("🧪 Testing Vision Alt Text Generation")
    print("=" * 50)

    # Test both providers if available
    providers = ["openai", "qwen"]

    for provider in providers:
        print(f"\n📊 Testing {provider.upper()} provider")
        print("-" * 30)

        try:
            vision_service = VisionService(provider=provider)

            if not vision_service.is_available():
                print(f"❌ {provider.upper()} provider not available")
                continue

            print(f"✅ {provider.upper()} provider initialized")
            print(f"   Provider: {vision_service.get_provider_name()}")

            for i, image in enumerate(test_images, 1):
                print(f"\n🖼️  Test Image {i}: {image['description']}")
                print(f"   URL: {image['url']}")
                print(f"   Context: {image['context']}")

                try:
                    # Generate alt text
                    alt_text = vision_service.generate_alt_text(
                        image["url"], context=image["context"]
                    )

                    print(f"   📝 Alt Text: {alt_text}")

                    # Analyze image content
                    analysis = vision_service.analyze_image(image["url"])
                    print(f"   🔍 Analysis: {json.dumps(analysis, indent=6)}")

                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")

        except Exception as e:
            print(f"❌ Failed to initialize {provider.upper()} provider: {str(e)}")


def test_ai_service_integration():
    """Test the AI service integration with vision capabilities"""

    print("\n🔗 Testing AI Service Integration")
    print("=" * 50)

    # Test data mimicking Contentful article structure
    test_articles = [
        {
            "title": "Maximizing ROI with Marketing Automation",
            "body": "Learn how to leverage marketing automation tools to increase your return on investment. This comprehensive guide covers best practices, common pitfalls, and proven strategies for success.",
            "hasImages": True,
            "altText": None,  # Missing alt text - should trigger generation
            "campaignTags": ["automation", "roi", "strategy"],
        },
        {
            "title": "Content Strategy for B2B Marketing",
            "body": "Develop a winning content strategy that converts prospects into customers. Explore the latest trends in B2B content marketing and how to measure success.",
            "hasImages": True,
            "altText": "Existing alt text",  # Has alt text - should not generate
            "campaignTags": ["content", "b2b", "strategy"],
        },
        {
            "title": "Analytics Dashboard Best Practices",
            "body": "Create effective analytics dashboards that drive decision-making. Learn to visualize key metrics and present data in actionable formats.",
            "hasImages": False,  # No images - should not generate alt text
            "altText": None,
            "campaignTags": ["analytics", "dashboard", "data"],
        },
    ]

    # Test with different AI providers
    ai_providers = ["openai", "local"]

    for provider in ai_providers:
        print(f"\n🤖 Testing with AI_PROVIDER={provider.upper()}")
        print("-" * 40)

        # Set environment variable for this test
        original_provider = os.getenv("AI_PROVIDER")
        os.environ["AI_PROVIDER"] = provider

        try:
            ai_service = AIService()

            for i, article in enumerate(test_articles, 1):
                print(f"\n📄 Article {i}: {article['title'][:50]}...")
                print(f"   Has Images: {article['hasImages']}")
                print(f"   Existing Alt Text: {article['altText'] or 'None'}")

                try:
                    # Test enrichment
                    enrichment = ai_service.enrich_content(article)
                    print(f"   ✅ Enrichment: SEO Score {enrichment.seo_score}")

                    # Test alt text generation
                    alt_text = ai_service.generate_alt_text(article)
                    if alt_text:
                        print(f"   📝 Generated Alt Text: {alt_text}")
                    else:
                        print("   ➖ No alt text generated (expected)")

                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")

        except Exception as e:
            print(f"❌ Failed to initialize AI service with {provider}: {str(e)}")

        finally:
            # Restore original provider
            if original_provider:
                os.environ["AI_PROVIDER"] = original_provider
            elif "AI_PROVIDER" in os.environ:
                del os.environ["AI_PROVIDER"]


def test_activation_endpoint():
    """Test the full activation endpoint with vision integration"""

    print("\n🚀 Testing Full Activation Endpoint")
    print("=" * 50)

    try:
        import requests

        # Test payload
        payload = {
            "entry_id": "2CYhWOGXOiQ5QCRnrZ3Mvo",  # One of our sample articles
            "enrichment_enabled": True,
            "marketo_list_id": "test-list-123",
        }

        # Make request to local FastAPI server
        response = requests.post(
            "http://localhost:8001/activate", json=payload, timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Activation successful!")
            print(f"   Processing time: {result['processing_time']:.3f}s")
            print(f"   Activation ID: {result['activation_id']}")

            # Check if alt text was generated
            if "enrichment" in result and result["enrichment"]:
                enrichment = result["enrichment"]
                if "generated_alt_text" in enrichment:
                    print(
                        f"   📝 Generated Alt Text: {enrichment['generated_alt_text']}"
                    )
                else:
                    print("   ➖ No alt text generated")

        else:
            print(f"❌ Activation failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ Endpoint test failed: {str(e)}")


def main():
    """Run all vision integration tests"""

    print("🎯 Vision Integration Test Suite")
    print("=" * 60)

    # Check environment setup
    print("\n🔧 Environment Check")
    print("-" * 20)
    print(f"OpenAI API Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"Vision Provider: {os.getenv('VISION_PROVIDER', 'openai')}")
    print(f"AI Provider: {os.getenv('AI_PROVIDER', 'openai')}")

    # Run tests
    test_sample_images()
    test_ai_service_integration()
    test_activation_endpoint()

    print("\n🎉 Test Suite Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
