"""
Secure environment variable loading utility
Prioritizes .env.local over .env for security
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def load_environment():
    """Load environment variables in secure priority order"""

    # Get the directory containing this file (backend/)
    backend_dir = Path(__file__).parent

    # Priority order: .env (template) first, then .env.local (dev only), then Render Secret Files (production)
    env_files = [
        backend_dir / ".env",  # Template values (safe to commit) - loaded first
        backend_dir / ".env.local",  # Real secrets (gitignored) - override templates
        Path(
            "/etc/secrets/.env"
        ),  # Render secret files (production) - highest priority
    ]

    loaded_files = []

    for env_file in env_files:
        if env_file.exists():
            load_dotenv(env_file, override=True)  # Later files override earlier ones
            loaded_files.append(str(env_file))

    # Log which files were loaded (but not their contents!)
    if loaded_files:
        print(f"✅ Loaded environment from: {', '.join(loaded_files)}")

        # Check if we're using real values or templates
        contentful_token = os.getenv("CONTENTFUL_ACCESS_TOKEN", "")
        contentful_space = os.getenv("CONTENTFUL_SPACE_ID", "")

        is_template = (
            contentful_token.startswith("your_")
            or contentful_space.startswith("your_")
            or len(contentful_token) < 10
            or len(contentful_space) < 5
        )

        if is_template:
            print(
                "⚠️  Using template environment values - add real secrets to .env.local"
            )
        else:
            print("🔒 Using real environment values from .env.local")
    else:
        print("❌ No environment files found")

    return loaded_files


if __name__ == "__main__":
    load_environment()
