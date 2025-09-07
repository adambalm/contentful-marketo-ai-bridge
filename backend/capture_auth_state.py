#!/usr/bin/env python3
"""
Capture Contentful authentication state for reuse in Playwright
Run this once when you're logged in to capture your session
"""

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


async def capture_contentful_auth():
    """
    Manual authentication capture process
    You'll need to log in manually, then we'll save the state
    """

    # Create auth directory
    auth_dir = Path("playwright_auth")
    auth_dir.mkdir(exist_ok=True)

    async with async_playwright() as p:
        # Check if we have a display available
        import os

        has_display = os.environ.get("DISPLAY") is not None

        if not has_display:
            print("⚠️  No X11 display detected. This is a headless server.")
            print("📋 We'll need to use a different approach for authentication...")
            print("\n💡 Alternative Options:")
            print("   1. Use SSH with X11 forwarding: ssh -X user@server")
            print("   2. Set up a virtual display with xvfb")
            print("   3. Use Contentful's authentication token directly")
            print(
                "\nFor now, let's skip the interactive login and create a manual auth method"
            )
            await browser.close() if "browser" in locals() else None
            return False

        # Launch browser in non-headless mode so you can log in
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()

        print("🚀 Opening Contentful login page...")
        await page.goto("https://app.contentful.com/login")

        print("\n📋 INSTRUCTIONS:")
        print("1. Please log in to Contentful in the browser window that just opened")
        print("2. Navigate to your space content types page")
        print("3. Once you're logged in and can see your content, press ENTER here")

        # Wait for user to log in
        input(
            "Press ENTER once you're logged in and can see your Contentful dashboard..."
        )

        # Test that we're actually logged in
        try:
            await page.goto(
                "https://app.contentful.com/spaces/ebgprhvsyuge/content_types"
            )
            await page.wait_for_selector("text=Article", timeout=5000)
            print("✅ Authentication verified - can access your space")
        except:
            print("❌ Could not verify authentication - make sure you're logged in")
            await browser.close()
            return False

        # Save the authentication state
        auth_file = auth_dir / "contentful_state.json"
        await context.storage_state(path=str(auth_file))

        print(f"💾 Authentication state saved to: {auth_file}")

        await browser.close()

        return True


async def test_saved_auth():
    """Test that the saved authentication state works"""

    auth_file = Path("playwright_auth/contentful_state.json")
    if not auth_file.exists():
        print("❌ No saved authentication state found")
        return False

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Load the saved authentication state
        context = await browser.new_context(storage_state=str(auth_file))
        page = await context.new_page()

        print("🧪 Testing saved authentication...")

        try:
            # Navigate to your content types page
            await page.goto(
                "https://app.contentful.com/spaces/ebgprhvsyuge/content_types"
            )
            await page.wait_for_selector("text=Article", timeout=10000)

            print("✅ Authentication test successful!")

            # Take a screenshot to verify
            screenshot_path = "test_auth_screenshot.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 Test screenshot saved to: {screenshot_path}")

            await browser.close()
            return True

        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            await browser.close()
            return False


async def take_content_model_screenshot():
    """Take screenshot of Article content model using saved authentication"""

    auth_file = Path("playwright_auth/contentful_state.json")
    if not auth_file.exists():
        print(
            "❌ No saved authentication state found. Run capture_contentful_auth() first"
        )
        return False

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=str(auth_file))
        page = await context.new_page()

        try:
            print("📸 Taking content model screenshot...")

            # Navigate to Article content type
            await page.goto(
                "https://app.contentful.com/spaces/ebgprhvsyuge/content_types/article"
            )

            # Wait for the page to load
            await page.wait_for_selector("text=Marketing Article", timeout=15000)

            # Take screenshot
            screenshot_path = "article_content_model.png"
            await page.screenshot(path=screenshot_path, full_page=True)

            print(f"✅ Screenshot saved to: {screenshot_path}")

            await browser.close()
            return True

        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            await browser.close()
            return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "capture":
            asyncio.run(capture_contentful_auth())
        elif sys.argv[1] == "test":
            asyncio.run(test_saved_auth())
        elif sys.argv[1] == "screenshot":
            asyncio.run(take_content_model_screenshot())
        else:
            print("Usage: python capture_auth_state.py [capture|test|screenshot]")
    else:
        print("Available commands:")
        print(
            "  python capture_auth_state.py capture    - Capture authentication state"
        )
        print("  python capture_auth_state.py test       - Test saved authentication")
        print(
            "  python capture_auth_state.py screenshot - Take content model screenshot"
        )
