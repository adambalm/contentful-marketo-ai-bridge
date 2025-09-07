#!/usr/bin/env python3
"""
Direct test of Ollama vision API to understand the correct format
"""

import base64

import requests


def test_ollama_vision_direct():
    """Test Ollama vision API directly"""

    print("🧪 Testing Ollama Vision API Directly")
    print("=" * 50)

    # Read and encode image
    with open("marketing_dashboard.png", "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    print(f"📸 Image size: {len(image_b64)} characters")

    # Test payload
    payload = {
        "model": "qwen2.5vl:7b",
        "prompt": "Describe what you see in this image in one sentence.",
        "images": [image_b64],
        "stream": False,
    }

    print("🔗 Making API request...")

    try:
        response = requests.post(
            "http://localhost:11434/api/generate", json=payload, timeout=60
        )

        print(f"📊 Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Response: {result.get('response', 'No response field')}")

            # Check other fields
            for key in ["model", "created_at", "done"]:
                if key in result:
                    print(f"{key}: {result[key]}")

        else:
            print("❌ Failed!")
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {e}")


if __name__ == "__main__":
    test_ollama_vision_direct()
