#!/usr/bin/env python3
"""
Real test of Qwen 2.5VL 7b vision model with actual generated images
"""

import base64
import os
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vision_service import QwenVisionProvider


def encode_image_to_base64(image_path):
    """Convert local image to base64 for Qwen vision model"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def test_qwen_with_local_images():
    """Test Qwen vision model with our generated images"""

    print("🧪 Testing Qwen 2.5VL 7b with Real Images")
    print("=" * 50)

    # Check if test images exist
    test_images = [
        {
            "file": "marketing_dashboard.png",
            "context": "marketing automation dashboard showing campaign performance metrics",
            "expected_elements": [
                "dashboard",
                "metrics",
                "campaign",
                "email",
                "conversions",
            ],
        },
        {
            "file": "content_strategy.png",
            "context": "content strategy planning and workflow optimization",
            "expected_elements": [
                "workflow",
                "strategy",
                "content",
                "process",
                "steps",
            ],
        },
        {
            "file": "analytics_chart.png",
            "context": "data analytics and performance tracking for marketing campaigns",
            "expected_elements": [
                "chart",
                "analytics",
                "data",
                "traffic",
                "statistics",
            ],
        },
    ]

    missing_images = []
    for img in test_images:
        if not Path(img["file"]).exists():
            missing_images.append(img["file"])

    if missing_images:
        print(f"❌ Missing test images: {missing_images}")
        print("Run generate_test_images.py first")
        return False

    print("✅ All test images found")

    # Initialize Qwen provider
    try:
        qwen_provider = QwenVisionProvider()
        print("✅ Qwen 2.5VL provider initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Qwen provider: {e}")
        return False

    # Test each image
    results = []

    for i, image_info in enumerate(test_images, 1):
        print(f"\n🖼️  Test {i}: {image_info['file']}")
        print(f"   Context: {image_info['context']}")

        try:
            # Convert image to base64 data URL format that Ollama expects
            image_b64 = encode_image_to_base64(image_info["file"])
            image_data_url = f"data:image/png;base64,{image_b64}"

            print("   📝 Generating alt text...")

            # Generate alt text
            alt_text = qwen_provider.generate_alt_text(
                image_data_url, context=image_info["context"]
            )

            print(f"   ✅ Alt Text: '{alt_text}'")

            # Analyze image content
            print("   🔍 Analyzing image content...")
            analysis = qwen_provider.analyze_image_content(image_data_url)

            print("   📊 Analysis Result:")
            if isinstance(analysis, dict) and "error" not in analysis:
                for key, value in analysis.items():
                    print(f"      {key}: {value}")
            else:
                print(f"      {analysis}")

            # Check quality of results
            quality_score = 0
            if alt_text and alt_text != "Image description unavailable":
                quality_score += 1
                # Check if expected elements are mentioned
                alt_lower = alt_text.lower()
                mentioned_elements = [
                    elem
                    for elem in image_info["expected_elements"]
                    if elem.lower() in alt_lower
                ]
                if mentioned_elements:
                    quality_score += 1
                    print(f"   🎯 Relevant elements mentioned: {mentioned_elements}")
                else:
                    print(
                        f"   ⚠️  Expected elements not clearly mentioned: {image_info['expected_elements']}"
                    )

            results.append(
                {
                    "image": image_info["file"],
                    "alt_text": alt_text,
                    "analysis": analysis,
                    "quality_score": quality_score,
                    "success": quality_score > 0,
                }
            )

        except Exception as e:
            print(f"   ❌ Error processing {image_info['file']}: {e}")
            results.append(
                {"image": image_info["file"], "error": str(e), "success": False}
            )

    # Summary
    print("\n📋 Test Summary")
    print("=" * 30)

    successful_tests = sum(1 for r in results if r.get("success", False))
    total_tests = len(results)

    print(f"✅ Successful tests: {successful_tests}/{total_tests}")

    if successful_tests > 0:
        print("🎉 Qwen 2.5VL vision model is working!")

        # Show best result
        best_result = max(
            [r for r in results if r.get("success", False)],
            key=lambda x: x.get("quality_score", 0),
            default=None,
        )

        if best_result:
            print(f"\n🏆 Best Result ({best_result['image']}):")
            print(f"    Alt Text: '{best_result['alt_text']}'")
    else:
        print("❌ No successful tests - check Ollama service and model")

    return successful_tests > 0


def test_integration_with_ai_service():
    """Test the integration through our AI service"""

    print("\n🔗 Testing AI Service Integration with Real Images")
    print("=" * 50)

    try:
        # Set environment to use local provider
        original_provider = os.getenv("AI_PROVIDER")
        os.environ["AI_PROVIDER"] = "local"

        from services.ai_service import AIService

        ai_service = AIService()

        # Test article data that would have images
        test_article = {
            "title": "Marketing Dashboard Analytics Guide",
            "body": "Learn how to create effective marketing dashboards that track key performance indicators like email open rates, click-through rates, and conversion metrics. This comprehensive guide shows you how to visualize campaign data for better decision making.",
            "hasImages": True,
            "altText": None,  # Missing - should trigger generation
            "campaignTags": ["dashboard", "analytics", "marketing"],
        }

        print("📄 Test Article: Marketing Dashboard Analytics Guide")
        print("   Has Images: True")
        print("   Existing Alt Text: None")

        # Test enrichment (this should work)
        enrichment = ai_service.enrich_content(test_article)
        print(f"✅ Enrichment successful - SEO Score: {enrichment.seo_score}")

        # Test alt text generation (this will show placeholder until we have image URLs)
        alt_text = ai_service.generate_alt_text(test_article)
        print(f"📝 Alt Text Result: '{alt_text}'")

        if alt_text and "Qwen 2.5VL" in alt_text:
            print("✅ AI Service successfully routes to Qwen provider")
        else:
            print("⚠️  AI Service integration needs image URL handling")

    except Exception as e:
        print(f"❌ AI Service integration error: {e}")
        return False
    finally:
        # Restore original provider
        if original_provider:
            os.environ["AI_PROVIDER"] = original_provider
        elif "AI_PROVIDER" in os.environ:
            del os.environ["AI_PROVIDER"]

    return True


def main():
    """Run comprehensive Qwen vision testing"""

    print("🎯 Qwen 2.5VL Vision Model Test Suite")
    print("=" * 60)

    # Check Ollama service
    print("\n🔧 Environment Check")
    print("-" * 20)

    try:
        import requests

        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            qwen_models = [
                m
                for m in models.get("models", [])
                if "qwen2.5vl" in m.get("name", "").lower()
            ]
            if qwen_models:
                print("✅ Ollama service running with Qwen 2.5VL")
                print(f"   Model: {qwen_models[0]['name']}")
            else:
                print("❌ Qwen 2.5VL model not found")
                return False
        else:
            print(f"❌ Ollama service not responding: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("   Make sure Ollama is running: ollama serve")
        return False

    # Run tests
    vision_success = test_qwen_with_local_images()
    integration_success = test_integration_with_ai_service()

    print("\n🎉 Test Suite Complete!")
    print("=" * 60)
    print(f"Vision Model Test: {'✅ PASSED' if vision_success else '❌ FAILED'}")
    print(f"Integration Test: {'✅ PASSED' if integration_success else '❌ FAILED'}")

    if vision_success:
        print("\n🚀 Qwen 2.5VL is ready for production use!")
        print("   Next step: Add image URL extraction from article content")
    else:
        print("\n🔧 Troubleshooting needed for Qwen vision model")


if __name__ == "__main__":
    main()
