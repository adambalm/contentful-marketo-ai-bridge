#!/usr/bin/env python3
"""
Create sample articles for testing live Contentful integration
"""

import os

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_sample_articles():
    """Create sample articles using the Management API"""

    space_id = os.getenv("CONTENTFUL_SPACE_ID")
    management_token = os.getenv("CONTENTFUL_MANAGEMENT_TOKEN")

    base_url = f"https://api.contentful.com/spaces/{space_id}/environments/master"
    headers = {
        "Authorization": f"Bearer {management_token}",
        "Content-Type": "application/vnd.contentful.management.v1+json",
    }

    print("🔧 Creating sample articles...")

    # Sample articles data - using correct field IDs
    sample_articles = [
        {
            "fields": {
                "title": {"en-US": "AI-Powered Marketing Automation Guide"},
                "body": {
                    "en-US": "This comprehensive guide explores how artificial intelligence is transforming marketing automation workflows. From lead scoring to personalized content delivery, AI enables marketers to create more effective, targeted campaigns that resonate with their audience and drive measurable results."
                },
                "aiSummary": {
                    "en-US": "Complete guide to AI marketing automation for modern marketers"
                },
                "campaignTags": {
                    "en-US": ["thought-leadership", "marketer", "awareness"]
                },
                "has_images": {"en-US": True},
                "alt_text": {
                    "en-US": "AI marketing automation dashboard showing campaign performance metrics"
                },
                "cta_text": {"en-US": "Download Free Guide"},
                "cta_url": {"en-US": "https://example.com/ai-marketing-guide"},
            }
        },
        {
            "fields": {
                "title": {"en-US": "Customer Success Story: 300% ROI Increase"},
                "body": {
                    "en-US": "Learn how TechCorp increased their marketing ROI by 300% using our AI content activation platform. This detailed case study breaks down their strategy, implementation process, and the remarkable results they achieved in just 6 months of using automated content workflows."
                },
                "aiSummary": {
                    "en-US": "TechCorp case study showing 300% ROI improvement with AI platform"
                },
                "campaignTags": {"en-US": ["case-study", "enterprise", "decision"]},
                "has_images": {"en-US": True},
                "alt_text": {"en-US": "Graph showing 300% ROI increase over 6 months"},
                "cta_text": {"en-US": "Schedule Demo"},
                "cta_url": {"en-US": "https://example.com/schedule-demo"},
            }
        },
        {
            "fields": {
                "title": {
                    "en-US": "Upcoming Webinar: Content Activation Best Practices"
                },
                "body": {
                    "en-US": "Join our experts for an exclusive webinar on content activation best practices. Discover proven strategies for maximizing content performance, automating distribution workflows, and measuring content impact across all your marketing channels."
                },
                "aiSummary": {
                    "en-US": "Expert webinar on content activation strategies and best practices"
                },
                "campaignTags": {
                    "en-US": ["webinar", "product-adoption", "consideration"]
                },
                "has_images": {"en-US": False},
                "cta_text": {"en-US": "Register Now"},
                "cta_url": {"en-US": "https://example.com/webinar-registration"},
            }
        },
    ]

    created_entries = []

    try:
        for i, article_data in enumerate(sample_articles):
            print(
                f"\n🔨 Creating article {i+1}: {article_data['fields']['title']['en-US']}"
            )

            # Create the entry
            response = requests.post(
                f"{base_url}/entries",
                headers={**headers, "X-Contentful-Content-Type": "article"},
                json=article_data,
            )

            if response.status_code == 201:
                entry = response.json()
                entry_id = entry["sys"]["id"]
                print(f"  ✅ Created entry: {entry_id}")

                # Publish the entry
                publish_headers = headers.copy()
                publish_headers["X-Contentful-Version"] = str(entry["sys"]["version"])

                publish_response = requests.put(
                    f"{base_url}/entries/{entry_id}/published", headers=publish_headers
                )

                if publish_response.status_code == 200:
                    print(f"  📡 Published entry: {entry_id}")
                    created_entries.append(entry_id)
                else:
                    print(f"  ❌ Failed to publish: {publish_response.status_code}")
                    print(f"     {publish_response.text}")
            else:
                print(f"  ❌ Failed to create entry: {response.status_code}")
                print(f"     {response.text}")

        print(f"\n🎉 Created {len(created_entries)} sample articles!")
        print(f"Entry IDs: {created_entries}")

        return created_entries

    except Exception as e:
        print(f"❌ Error creating sample articles: {e}")
        import traceback

        traceback.print_exc()
        return []


if __name__ == "__main__":
    entry_ids = create_sample_articles()
    if entry_ids:
        print("\n✅ Success! You can now test with these entry IDs:")
        for entry_id in entry_ids:
            print(f"  - {entry_id}")
    else:
        print("\n❌ No articles were created successfully")
