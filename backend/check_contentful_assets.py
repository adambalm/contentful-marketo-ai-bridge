#!/usr/bin/env python3
"""
Check what assets exist in Contentful and their publishing status
"""

import os
import sys
from pathlib import Path

import requests

# Add parent directory to path for secure environment loading
sys.path.insert(0, str(Path(__file__).parent))
from load_env import load_environment

# Load environment variables securely
load_environment()


def check_assets():
    """Check all assets in Contentful space"""
    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")
    access_token = os.getenv("CONTENTFUL_ACCESS_TOKEN")

    print("🔍 Checking Contentful Assets")
    print("=" * 40)

    # Check with Management API (shows all assets including unpublished)
    headers = {
        "Authorization": f"Bearer {management_token}",
        "Content-Type": "application/vnd.contentful.management.v1+json",
    }

    response = requests.get(
        f"https://api.contentful.com/spaces/{space_id}/assets", headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        assets = data.get("items", [])
        print(f"📋 Found {len(assets)} total assets (including unpublished)")

        for asset in assets:
            asset_id = asset["sys"]["id"]
            version = asset["sys"]["version"]
            published_version = asset["sys"].get("publishedVersion")
            title = asset.get("fields", {}).get("title", {}).get("en-US", "No title")

            status = "Published" if published_version else "Draft"
            print(f"   • {title} (ID: {asset_id})")
            print(f"     Status: {status}, Version: {version}")

            # Check if file is processed
            file_field = asset.get("fields", {}).get("file", {}).get("en-US")
            if file_field:
                if "url" in file_field:
                    print(f"     File: ✅ Processed - {file_field['url']}")
                else:
                    print("     File: ⏳ Processing...")
            else:
                print("     File: ❌ Missing")
            print()
    else:
        print(f"❌ Failed to get assets: {response.status_code} - {response.text}")
        return

    # Check with Delivery API (shows only published assets)
    print("\n🌐 Published Assets (Delivery API):")
    delivery_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.contentful.delivery.v1+json",
    }

    delivery_response = requests.get(
        f"https://cdn.contentful.com/spaces/{space_id}/assets", headers=delivery_headers
    )

    if delivery_response.status_code == 200:
        delivery_data = delivery_response.json()
        published_assets = delivery_data.get("items", [])
        print(f"📋 Found {len(published_assets)} published assets")

        for asset in published_assets:
            title = asset.get("fields", {}).get("title", "No title")
            file_url = asset.get("fields", {}).get("file", {}).get("url", "No URL")
            print(f"   • {title}: https:{file_url}")
    else:
        print(f"❌ Failed to get published assets: {delivery_response.status_code}")


def publish_unpublished_assets():
    """Publish any unpublished assets"""
    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")

    headers = {
        "Authorization": f"Bearer {management_token}",
        "Content-Type": "application/vnd.contentful.management.v1+json",
    }

    # Get all assets
    response = requests.get(
        f"https://api.contentful.com/spaces/{space_id}/assets", headers=headers
    )

    if response.status_code != 200:
        print(f"❌ Failed to get assets: {response.status_code}")
        return False

    assets = response.json().get("items", [])
    unpublished = []

    for asset in assets:
        if not asset["sys"].get("publishedVersion"):
            # Check if file is processed
            file_field = asset.get("fields", {}).get("file", {}).get("en-US")
            if file_field and "url" in file_field:
                unpublished.append(asset)

    if unpublished:
        print(f"\n🔄 Publishing {len(unpublished)} processed but unpublished assets...")

        for asset in unpublished:
            asset_id = asset["sys"]["id"]
            version = asset["sys"]["version"]
            title = asset.get("fields", {}).get("title", {}).get("en-US", asset_id)

            publish_response = requests.put(
                f"https://api.contentful.com/spaces/{space_id}/assets/{asset_id}/published",
                headers={
                    "Authorization": f"Bearer {management_token}",
                    "X-Contentful-Version": str(version),
                },
            )

            if publish_response.status_code == 200:
                print(f"   ✅ Published: {title}")
            else:
                print(f"   ❌ Failed to publish {title}: {publish_response.status_code}")

        return True
    else:
        print("\n✅ All processed assets are already published")
        return True


def main():
    check_assets()
    publish_unpublished_assets()


if __name__ == "__main__":
    main()
