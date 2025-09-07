#!/usr/bin/env python3
"""
Generate appropriate marketing images for live Contentful articles.
Creates professional images that match article content for vision testing.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from load_env import load_environment

# Load environment
load_environment()


def create_marketing_automation_guide_image():
    """Create image for 'AI-Powered Marketing Automation Guide'"""

    # Create figure with professional marketing design
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor("#f8f9fa")

    # Title
    ax.text(
        0.5,
        0.9,
        "AI-Powered Marketing Automation",
        ha="center",
        va="center",
        fontsize=24,
        fontweight="bold",
        color="#2c3e50",
        transform=ax.transAxes,
    )

    ax.text(
        0.5,
        0.85,
        "Complete Implementation Guide",
        ha="center",
        va="center",
        fontsize=16,
        color="#34495e",
        transform=ax.transAxes,
    )

    # Create workflow diagram
    workflow_steps = [
        "Lead\nCapture",
        "AI\nScoring",
        "Automated\nNurturing",
        "Content\nPersonalization",
        "Campaign\nOptimization",
    ]

    colors = ["#3498db", "#e74c3c", "#f39c12", "#27ae60", "#9b59b6"]

    y_pos = 0.6
    x_positions = np.linspace(0.1, 0.9, len(workflow_steps))

    for i, (step, color, x_pos) in enumerate(zip(workflow_steps, colors, x_positions)):
        # Draw circle for step
        circle = plt.Circle(
            (x_pos, y_pos), 0.08, color=color, alpha=0.8, transform=ax.transAxes
        )
        ax.add_patch(circle)

        # Add step text
        ax.text(
            x_pos,
            y_pos,
            step,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="white",
            transform=ax.transAxes,
        )

        # Add arrow to next step
        if i < len(workflow_steps) - 1:
            ax.annotate(
                "",
                xy=(x_positions[i + 1] - 0.08, y_pos),
                xytext=(x_pos + 0.08, y_pos),
                arrowprops=dict(arrowstyle="->", lw=2, color="#34495e"),
                transform=ax.transAxes,
            )

    # Add key metrics
    metrics = [
        ("Lead Quality Score", "+85%"),
        ("Conversion Rate", "+42%"),
        ("Time to Close", "-60%"),
        ("Marketing ROI", "+156%"),
    ]

    y_start = 0.35
    for i, (metric, value) in enumerate(metrics):
        y_pos = y_start - i * 0.06
        ax.text(
            0.25,
            y_pos,
            metric + ":",
            ha="left",
            va="center",
            fontsize=12,
            color="#2c3e50",
            transform=ax.transAxes,
        )
        ax.text(
            0.65,
            y_pos,
            value,
            ha="left",
            va="center",
            fontsize=12,
            fontweight="bold",
            color="#27ae60",
            transform=ax.transAxes,
        )

    # Remove axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Save image
    filename = "marketing_automation_guide.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor="#f8f9fa")
    plt.close()

    print(f"✅ Created {filename}: Professional marketing automation workflow diagram")
    return filename


def create_roi_success_story_image():
    """Create image for 'Customer Success Story: 300% ROI Increase'"""

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor("#ffffff")

    # Title
    ax.text(
        0.5,
        0.9,
        "TechCorp Success Story",
        ha="center",
        va="center",
        fontsize=24,
        fontweight="bold",
        color="#2c3e50",
        transform=ax.transAxes,
    )

    ax.text(
        0.5,
        0.85,
        "300% ROI Increase with AI Content Activation",
        ha="center",
        va="center",
        fontsize=16,
        color="#e74c3c",
        transform=ax.transAxes,
    )

    # Create before/after comparison chart
    categories = [
        "Lead\nGeneration",
        "Content\nEngagement",
        "Conversion\nRate",
        "Customer\nRetention",
    ]
    before_values = [100, 100, 100, 100]  # Baseline
    after_values = [250, 180, 320, 190]  # Improvements

    x = np.arange(len(categories))
    width = 0.35

    # Create bars
    bars1 = ax.bar(
        [i - width / 2 for i in x],
        before_values,
        width,
        label="Before AI",
        color="#bdc3c7",
        alpha=0.8,
    )
    bars2 = ax.bar(
        [i + width / 2 for i in x],
        after_values,
        width,
        label="After AI",
        color="#e74c3c",
        alpha=0.9,
    )

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 5,
                f"{int(height)}%",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

    # Customize chart
    ax.set_ylabel("Performance Index (%)", fontsize=12)
    ax.set_title(
        "Performance Metrics: Before vs After AI Implementation",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend(loc="upper left")
    ax.set_ylim(0, 350)

    # Add grid
    ax.grid(axis="y", alpha=0.3)
    ax.set_facecolor("#f8f9fa")

    # Save image
    filename = "roi_success_story.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()

    print(f"✅ Created {filename}: Customer success metrics comparison chart")
    return filename


def create_webinar_promotional_image():
    """Create image for 'Upcoming Webinar: Content Activation Best Practices'"""

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor("#2c3e50")

    # Main title
    ax.text(
        0.5,
        0.8,
        "LIVE WEBINAR",
        ha="center",
        va="center",
        fontsize=20,
        fontweight="bold",
        color="#f39c12",
        transform=ax.transAxes,
    )

    ax.text(
        0.5,
        0.7,
        "Content Activation Best Practices",
        ha="center",
        va="center",
        fontsize=22,
        fontweight="bold",
        color="white",
        transform=ax.transAxes,
    )

    ax.text(
        0.5,
        0.62,
        "Master AI-Driven Content Strategy",
        ha="center",
        va="center",
        fontsize=14,
        color="#ecf0f1",
        transform=ax.transAxes,
    )

    # Event details box
    box_props = dict(boxstyle="round,pad=0.02", facecolor="white", alpha=0.9)

    details = [
        "📅 Date: March 15, 2024",
        "🕒 Time: 2:00 PM EST",
        "👥 Expert Panel Discussion",
        "🎯 Live Q&A Session",
        "📊 Real Campaign Examples",
    ]

    y_start = 0.45
    for i, detail in enumerate(details):
        ax.text(
            0.5,
            y_start - i * 0.06,
            detail,
            ha="center",
            va="center",
            fontsize=12,
            color="#2c3e50",
            transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.01", facecolor="white", alpha=0.8),
        )

    # Call to action
    ax.text(
        0.5,
        0.05,
        "Register Free → contentful.com/webinar",
        ha="center",
        va="center",
        fontsize=16,
        fontweight="bold",
        color="#f39c12",
        transform=ax.transAxes,
        bbox=dict(boxstyle="round,pad=0.02", facecolor="#34495e", alpha=0.9),
    )

    # Remove axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    filename = "webinar_promotion.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor="#2c3e50")
    plt.close()

    print(f"✅ Created {filename}: Professional webinar promotional design")
    return filename


def test_generated_images_with_vision():
    """Test the generated images with our vision processing"""

    print("\n🎯 Testing Generated Images with Vision Processing")
    print("=" * 55)

    import base64

    from services.ai_service import AIService

    ai_service = AIService()

    # Test each generated image
    image_files = [
        "marketing_automation_guide.png",
        "roi_success_story.png",
        "webinar_promotion.png",
    ]

    article_contexts = [
        "AI-powered marketing automation guide showing workflow implementation",
        "Customer success story demonstrating 300% ROI increase from AI marketing",
        "Upcoming webinar promotion for content activation best practices",
    ]

    for img_file, context in zip(image_files, article_contexts):
        if Path(img_file).exists():
            print(f"\n📊 Testing {img_file}")
            print(f"   Context: {context}")

            # Read as base64 for local vision processing
            with open(img_file, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("ascii")

            data_url = f"data:image/png;base64,{image_data}"

            # Create test article data
            test_article = {
                "title": context,
                "body": f"<img src='{data_url}' alt='' />",
                "has_images": True,
                "campaign_tags": ["marketing", "automation"],
            }

            try:
                alt_text = ai_service.generate_alt_text(test_article)
                print(f"   🎯 Generated Alt Text: {alt_text}")
            except Exception as e:
                print(f"   ❌ Vision processing error: {e}")


if __name__ == "__main__":
    print("🎨 Generating Professional Marketing Images")
    print("=" * 50)

    # Generate images for each article type
    images_created = []
    images_created.append(create_marketing_automation_guide_image())
    images_created.append(create_roi_success_story_image())
    images_created.append(create_webinar_promotional_image())

    print(f"\n📸 Created {len(images_created)} professional marketing images")

    # Test with vision processing
    test_generated_images_with_vision()

    print("\n🏁 Image Generation Complete!")
    print("\nNext steps:")
    print("1. These images can be uploaded to Contentful articles")
    print("2. Vision processing can generate contextual alt text")
    print("3. Full end-to-end workflow testing enabled")
