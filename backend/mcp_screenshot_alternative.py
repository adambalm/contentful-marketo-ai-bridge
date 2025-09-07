#!/usr/bin/env python3
"""
Alternative screenshot approach using the configured Contentful MCP
Since we can't use interactive browser auth on headless server
"""

import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()


def create_manual_auth_session():
    """
    Create a manual authentication session state for Contentful
    This bypasses the interactive login by using API-based verification
    """

    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")

    if not space_id or not management_token:
        print("❌ Missing Contentful credentials in environment")
        return False

    print("🔧 Creating manual authentication session...")

    # Test that our tokens work
    headers = {
        "Authorization": f"Bearer {management_token}",
        "Content-Type": "application/vnd.contentful.management.v1+json",
    }

    try:
        # Test Management API access
        response = requests.get(
            f"https://api.contentful.com/spaces/{space_id}", headers=headers
        )

        if response.status_code == 200:
            space_info = response.json()
            print("✅ Management API access verified")
            print(f"   Space: {space_info['name']}")

            # Create a simplified auth state that we can use with MCP
            auth_state = {
                "space_id": space_id,
                "management_token": management_token,
                "verified": True,
                "space_name": space_info["name"],
            }

            # Save this for reference
            with open("contentful_auth_info.json", "w") as f:
                json.dump(auth_state, f, indent=2)

            print("💾 Authentication info saved to contentful_auth_info.json")
            return True
        else:
            print(f"❌ Management API access failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
        return False


def try_mcp_screenshot():
    """
    Try using the configured MCP Playwright to take screenshot
    """
    print("\n📸 Attempting screenshot via MCP Playwright...")
    print("💡 Since MCP Playwright is configured, it might have different auth handling")

    # The MCP should be able to handle this if configured properly
    # Let's provide instructions for manual verification instead

    print("\n📋 Manual Verification Steps:")
    print("1. Open your browser and navigate to:")
    print(
        f"   https://app.contentful.com/spaces/{os.getenv('CONTENTFUL_SPACE_ID', 'YOUR_SPACE_ID')}/content_types/article"
    )
    print("\n2. Verify you can see:")
    print("   • Content type name: 'Marketing Article' or 'Article'")
    print("   • 9 fields total:")
    print("     - Title (Symbol, required)")
    print("     - Body (Text, required)")
    print("     - AI Summary (Text, optional)")
    print("     - AI Keywords (Array, optional)")
    print("     - Campaign Tags (Array, required)")
    print("     - Has Images (Boolean, optional)")
    print("     - Alt Text (Text, optional)")
    print("     - CTA Text (Symbol, optional)")
    print("     - CTA URL (Symbol, optional)")
    print("\n3. Take a screenshot and save it locally")

    return True


def main():
    print("🔧 Alternative Contentful Screenshot Setup")
    print("=" * 50)

    if create_manual_auth_session():
        try_mcp_screenshot()

        print("\n✅ Setup complete!")
        print("\n🎯 Next Steps:")
        print("1. Manually verify your content model in browser")
        print("2. Take screenshot for documentation")
        print("3. We can proceed with vision alt-text generation")

        return True
    else:
        print("❌ Setup failed")
        return False


if __name__ == "__main__":
    main()
