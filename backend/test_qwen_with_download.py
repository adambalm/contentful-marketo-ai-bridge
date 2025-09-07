#!/usr/bin/env python3
"""
Test Qwen vision model by downloading Contentful images locally first
"""

import os
import sys
import tempfile
from pathlib import Path

import requests

# Add parent directory to path for secure environment loading
sys.path.insert(0, str(Path(__file__).parent))
from load_env import load_environment
from services.vision_service import VisionService

# Load environment variables securely
load_environment()


def test_qwen_with_download():
    """Test Qwen by downloading and processing images locally"""
    print("🔬 Testing Qwen Vision with Downloaded Images")
    print("=" * 50)

    vision = VisionService()

    # Test images from Contentful
    test_images = [
        {
            "name": "Marketing Automation",
            "url": "https://images.ctfassets.net/ebgprhvsyuge/1qj41vB3rIK9k3pqps0jBi/b817f2719906393140041704328c9235/marketing-automation-hero.png",
        },
        {
            "name": "Content Strategy",
            "url": "https://images.ctfassets.net/ebgprhvsyuge/3q4mCwl8JCljWrK1uKWSHA/3d4cbba49412b987df0635d59a582d1c/content-strategy-guide.png",
        },
        {
            "name": "Analytics Dashboard",
            "url": "https://images.ctfassets.net/ebgprhvsyuge/1eSv0JiChyh87p7Em7MrRO/ebe9237eef0106b3de40950bf1aa53f4/analytics-dashboard-preview.png",
        },
    ]

    success_count = 0

    for image_info in test_images:
        print(f"\n🖼️  Testing: {image_info['name']}")
        print(f"📁 URL: {image_info['url']}")

        try:
            # Download image to temporary file
            response = requests.get(image_info["url"], stream=True)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_path = temp_file.name

            print(f"📥 Downloaded to: {temp_path}")

            # Generate alt text using local file
            alt_text = vision.generate_alt_text(temp_path)
            print(f"🤖 Alt Text: {alt_text}")

            # Evaluate quality
            if (
                len(alt_text) > 10
                and alt_text != "Remote images not yet supported in local model"
            ):
                print("✅ Success: Professional alt text generated")
                success_count += 1
            else:
                print("⚠️  Warning: Basic or no alt text")

            # Clean up
            os.unlink(temp_path)

        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n🎯 Test Results:")
    print(f"   • Images tested: {len(test_images)}")
    print(f"   • Successful generations: {success_count}")
    print(f"   • Success rate: {success_count/len(test_images)*100:.1f}%")

    if success_count > 0:
        print("✅ Qwen Vision working with local files")
        return True
    else:
        print("❌ Qwen Vision needs configuration")
        return False


def main():
    return test_qwen_with_download()


if __name__ == "__main__":
    main()
