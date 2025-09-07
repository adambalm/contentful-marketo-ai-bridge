#!/usr/bin/env python3
"""
Test complete activation workflow with live Contentful integration
"""

import json

import requests
from dotenv import load_dotenv

load_dotenv()


def test_live_activation():
    """Test the complete /activate endpoint with real Contentful data"""

    # Test with our first sample article
    test_entry_id = "1VDVr3iJrsKzI8Ay8yPiFv"

    payload = {"entry_id": test_entry_id, "marketo_list_id": "ML_DEMO_001"}

    print("🧪 Testing complete activation workflow...")
    print(f"Entry ID: {test_entry_id}")
    print("Expected: AI-Powered Marketing Automation Guide")

    try:
        # Test the activation endpoint
        response = requests.post(
            "http://localhost:8001/activate", json=payload, timeout=30
        )

        print(f"\n📊 Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            print("✅ Activation successful!")

            # Debug: show actual response structure
            print("\n🔍 Full Response Structure:")
            print(json.dumps(result, indent=2)[:500] + "...")

            print("\n📋 Result Summary:")
            print(f"  • Activation ID: {result.get('activation_id', 'N/A')}")
            print(f"  • Entry ID: {result.get('entry_id', 'N/A')}")
            print(f"  • Status: {result.get('status', 'N/A')}")
            print(f"  • Processing Time: {result.get('processing_time', 'N/A')}s")
        else:
            print("❌ Activation failed!")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the backend server running?")
        print("💡 Try: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_live_activation()
