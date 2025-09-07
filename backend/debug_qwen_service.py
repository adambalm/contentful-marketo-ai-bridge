#!/usr/bin/env python3
"""
Debug the Qwen vision service wrapper
"""

import base64
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vision_service import QwenVisionProvider


def debug_qwen_service():
    """Debug the Qwen service step by step"""

    print("🔍 Debug Qwen Vision Service")
    print("=" * 40)

    # Initialize provider
    try:
        provider = QwenVisionProvider()
        print("✅ QwenVisionProvider initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return

    # Read image
    try:
        with open("marketing_dashboard.png", "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")
        print(f"✅ Image loaded: {len(image_b64)} characters")
    except Exception as e:
        print(f"❌ Failed to load image: {e}")
        return

    # Test 1: Direct base64 (as direct API worked)
    print("\n🧪 Test 1: Direct base64")
    try:
        alt_text = provider.generate_alt_text(image_b64, "marketing dashboard")
        print(f"Result: {alt_text}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Data URL format
    print("\n🧪 Test 2: Data URL format")
    try:
        data_url = f"data:image/png;base64,{image_b64}"
        alt_text = provider.generate_alt_text(data_url, "marketing dashboard")
        print(f"Result: {alt_text}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 3: Check what the service is actually sending
    print("\n🧪 Test 3: Debug API call")
    try:

        import requests

        payload = {
            "model": "qwen2.5vl:7b",
            "prompt": "Describe this image in one sentence.",
            "images": [image_b64],
            "stream": False,
        }

        print("Making direct request...")
        response = requests.post(
            "http://localhost:11434/api/generate", json=payload, timeout=30
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response', 'No response field')}")
        else:
            print(f"Error response: {response.text}")

    except Exception as e:
        print(f"Debug API call failed: {e}")


if __name__ == "__main__":
    debug_qwen_service()
