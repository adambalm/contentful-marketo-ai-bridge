#!/usr/bin/env python3
"""
Generate test images for vision model testing
Creates realistic marketing-related images for alt text generation
"""


from PIL import Image, ImageDraw, ImageFont


def create_marketing_dashboard_image():
    """Create a mock marketing dashboard image"""

    # Create image
    width, height = 800, 600
    img = Image.new("RGB", (width, height), color="#f8f9fa")
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([0, 0, width, 80], fill="#0066cc")

    try:
        # Try to use a system font, fall back to default if not available
        try:
            font_large = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
            )
            font_medium = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16
            )
            font_small = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12
            )
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Title
        draw.text(
            (20, 25), "Marketing Campaign Dashboard", fill="white", font=font_large
        )

        # Metrics boxes
        metrics = [
            ("Email Opens", "12,458", "#28a745"),
            ("Click-through Rate", "3.2%", "#17a2b8"),
            ("Conversions", "284", "#ffc107"),
            ("ROI", "+156%", "#dc3545"),
        ]

        x_start = 50
        y_start = 120
        box_width = 160
        box_height = 100

        for i, (title, value, color) in enumerate(metrics):
            x = x_start + (i % 2) * (box_width + 50)
            y = y_start + (i // 2) * (box_height + 30)

            # Draw metric box
            draw.rectangle(
                [x, y, x + box_width, y + box_height], fill=color, outline="#dee2e6"
            )
            draw.text((x + 10, y + 15), title, fill="white", font=font_medium)
            draw.text((x + 10, y + 50), value, fill="white", font=font_large)

        # Chart area placeholder
        chart_x, chart_y = 450, 120
        chart_width, chart_height = 300, 200
        draw.rectangle(
            [chart_x, chart_y, chart_x + chart_width, chart_y + chart_height],
            fill="white",
            outline="#dee2e6",
        )
        draw.text(
            (chart_x + 50, chart_y + 20),
            "Campaign Performance",
            fill="#333",
            font=font_medium,
        )

        # Draw simple line chart
        points = [
            (chart_x + 20, chart_y + 150),
            (chart_x + 80, chart_y + 120),
            (chart_x + 140, chart_y + 80),
            (chart_x + 200, chart_y + 60),
            (chart_x + 260, chart_y + 40),
        ]
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill="#0066cc", width=3)
            draw.ellipse(
                [
                    points[i][0] - 3,
                    points[i][1] - 3,
                    points[i][0] + 3,
                    points[i][1] + 3,
                ],
                fill="#0066cc",
            )

    except Exception:
        # Fallback if fonts fail
        draw.text((20, 25), "Marketing Campaign Dashboard", fill="white")
        draw.text((50, 150), "Email Opens: 12,458", fill="#333")
        draw.text((50, 200), "CTR: 3.2%", fill="#333")
        draw.text((50, 250), "Conversions: 284", fill="#333")

    return img


def create_content_strategy_image():
    """Create a content strategy workflow image"""

    width, height = 600, 400
    img = Image.new("RGB", (width, height), color="#ffffff")
    draw = ImageDraw.Draw(img)

    try:
        try:
            font_large = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20
            )
            font_medium = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14
            )
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()

        # Title
        draw.text((50, 30), "Content Strategy Workflow", fill="#333", font=font_large)

        # Workflow steps
        steps = [
            ("1. Research", "#e74c3c"),
            ("2. Plan", "#f39c12"),
            ("3. Create", "#27ae60"),
            ("4. Publish", "#3498db"),
            ("5. Analyze", "#9b59b6"),
        ]

        step_width = 100
        step_height = 60
        y_pos = 150
        spacing = 10

        for i, (step, color) in enumerate(steps):
            x_pos = 50 + i * (step_width + spacing)

            # Draw step box
            draw.rectangle(
                [x_pos, y_pos, x_pos + step_width, y_pos + step_height],
                fill=color,
                outline="#bdc3c7",
            )
            draw.text((x_pos + 10, y_pos + 20), step, fill="white", font=font_medium)

            # Draw arrow between steps
            if i < len(steps) - 1:
                arrow_start = x_pos + step_width + 5
                arrow_end = arrow_start + spacing - 10
                arrow_y = y_pos + step_height // 2
                draw.line(
                    [arrow_start, arrow_y, arrow_end, arrow_y], fill="#7f8c8d", width=2
                )
                draw.polygon(
                    [
                        arrow_end,
                        arrow_y - 5,
                        arrow_end,
                        arrow_y + 5,
                        arrow_end + 5,
                        arrow_y,
                    ],
                    fill="#7f8c8d",
                )

    except Exception:
        # Fallback
        draw.text((50, 30), "Content Strategy Workflow", fill="#333")
        draw.text(
            (50, 150), "Research -> Plan -> Create -> Publish -> Analyze", fill="#333"
        )

    return img


def create_analytics_chart_image():
    """Create an analytics chart image"""

    width, height = 500, 350
    img = Image.new("RGB", (width, height), color="#f8f9fa")
    draw = ImageDraw.Draw(img)

    try:
        try:
            font_large = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18
            )
            font_medium = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12
            )
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()

        # Title
        draw.text(
            (50, 20), "Website Traffic Analytics", fill="#2c3e50", font=font_large
        )

        # Chart area
        chart_x, chart_y = 50, 80
        chart_width, chart_height = 400, 200

        # Draw chart background
        draw.rectangle(
            [chart_x, chart_y, chart_x + chart_width, chart_y + chart_height],
            fill="white",
            outline="#bdc3c7",
        )

        # Draw grid lines
        for i in range(1, 5):
            y = chart_y + i * (chart_height // 5)
            draw.line([chart_x, y, chart_x + chart_width, y], fill="#ecf0f1", width=1)

        # Draw bars
        bars = [
            ("Jan", 120, "#3498db"),
            ("Feb", 85, "#e74c3c"),
            ("Mar", 200, "#2ecc71"),
            ("Apr", 150, "#f39c12"),
            ("May", 180, "#9b59b6"),
            ("Jun", 220, "#1abc9c"),
        ]

        bar_width = 50
        max_value = 250
        spacing = 10

        for i, (month, value, color) in enumerate(bars):
            x = chart_x + 20 + i * (bar_width + spacing)
            bar_height = int((value / max_value) * (chart_height - 40))
            y = chart_y + chart_height - 20 - bar_height

            # Draw bar
            draw.rectangle(
                [x, y, x + bar_width, chart_y + chart_height - 20], fill=color
            )

            # Draw month label
            draw.text(
                (x + 15, chart_y + chart_height - 15),
                month,
                fill="#2c3e50",
                font=font_medium,
            )

            # Draw value label
            draw.text((x + 10, y - 20), str(value), fill="#2c3e50", font=font_medium)

    except Exception:
        # Fallback
        draw.text((50, 20), "Website Traffic Analytics", fill="#333")
        draw.rectangle([50, 80, 450, 280], fill="white", outline="#ccc")
        draw.text((60, 100), "Monthly visitor data visualization", fill="#333")

    return img


def save_test_images():
    """Generate and save test images"""

    images = [
        (
            "marketing_dashboard.png",
            create_marketing_dashboard_image(),
            "Marketing campaign dashboard showing email opens, click-through rates, conversions and ROI metrics",
        ),
        (
            "content_strategy.png",
            create_content_strategy_image(),
            "Content strategy workflow diagram showing research, planning, creation, publishing and analysis phases",
        ),
        (
            "analytics_chart.png",
            create_analytics_chart_image(),
            "Website traffic analytics bar chart displaying monthly visitor statistics",
        ),
    ]

    print("🎨 Generating test images for vision model testing...")

    for filename, img, description in images:
        img.save(filename)
        print(f"✅ Created {filename}: {description}")

    return [f for f, _, _ in images]


if __name__ == "__main__":
    image_files = save_test_images()
    print(f"\n🖼️  Generated {len(image_files)} test images")
    print("Ready for vision model testing!")
