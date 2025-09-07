#!/usr/bin/env python3
"""
Update sample articles to include AI keywords that are currently empty
"""

import os

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def update_article_with_keywords(entry_id, keywords):
    """Update a specific article with AI keywords"""

    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")

    base_url = f"https://api.contentful.com/spaces/{space_id}/environments/master"
    headers = {
        "Authorization": f"Bearer {management_token}",
        "Content-Type": "application/vnd.contentful.management.v1+json",
    }

    try:
        # Get current entry
        response = requests.get(f"{base_url}/entries/{entry_id}", headers=headers)
        if response.status_code != 200:
            print(f"❌ Failed to get entry {entry_id}: {response.status_code}")
            return False

        entry = response.json()
        print(f"📝 Updating {entry['fields']['title']['en-US']}...")

        # Update the aiKeywords field
        entry["fields"]["aiKeywords"] = {"en-US": keywords}

        # Update the entry
        update_headers = headers.copy()
        update_headers["X-Contentful-Version"] = str(entry["sys"]["version"])

        update_response = requests.put(
            f"{base_url}/entries/{entry_id}",
            headers=update_headers,
            json={"fields": entry["fields"]},
        )

        if update_response.status_code == 200:
            updated_entry = update_response.json()

            # Publish the updated entry
            publish_headers = headers.copy()
            publish_headers["X-Contentful-Version"] = str(
                updated_entry["sys"]["version"]
            )

            publish_response = requests.put(
                f"{base_url}/entries/{entry_id}/published", headers=publish_headers
            )

            if publish_response.status_code == 200:
                print(f"  ✅ Updated and published with keywords: {keywords}")
                return True
            else:
                print(f"  ❌ Failed to publish: {publish_response.status_code}")
                return False
        else:
            print(f"  ❌ Failed to update: {update_response.status_code}")
            print(f"     {update_response.text}")
            return False

    except Exception as e:
        print(f"❌ Error updating entry {entry_id}: {e}")
        return False


def update_all_sample_articles():
    """Update all sample articles with appropriate AI keywords"""

    # Article 1: AI Marketing Guide
    success1 = update_article_with_keywords(
        "1VDVr3iJrsKzI8Ay8yPiFv",
        [
            "artificial intelligence",
            "marketing automation",
            "lead scoring",
            "personalization",
            "campaign targeting",
        ],
    )

    # Article 2: Customer Success Story
    success2 = update_article_with_keywords(
        "3mrhiMCniMWTbzVaRQmf93",
        [
            "ROI",
            "case study",
            "enterprise",
            "AI platform",
            "content activation",
            "marketing results",
        ],
    )

    # Article 3: Webinar Announcement
    success3 = update_article_with_keywords(
        "3i3yuqnbPcqv9qFp7zGcwE",
        [
            "webinar",
            "content activation",
            "best practices",
            "marketing channels",
            "content performance",
        ],
    )

    successful_updates = sum([success1, success2, success3])
    print(f"\n📊 Updated {successful_updates}/3 articles with AI keywords")

    return successful_updates == 3


if __name__ == "__main__":
    print("🔧 Updating sample articles with AI keywords...")
    if update_all_sample_articles():
        print("✅ All articles updated successfully!")
    else:
        print("❌ Some updates failed")
