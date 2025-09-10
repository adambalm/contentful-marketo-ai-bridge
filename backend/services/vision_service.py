"""
Vision AI service for generating alt text from images
Supports both GPT-4o (production) and Qwen 2.5VL 7b (local)
Includes UTF-16 surrogate validation safeguards.
"""

import logging
import os
import sys
from abc import ABC, abstractmethod

# Load environment variables securely
from pathlib import Path
from typing import Any

import requests

# Import surrogate validation safeguards
from .validation_utils import (
    pre_flight_api_validation,
    validate_base64_string,
    validate_string_for_surrogates,
)

sys.path.insert(0, str(Path(__file__).parent.parent))
from load_env import load_environment

load_environment()

logger = logging.getLogger(__name__)


class VisionProvider(ABC):
    """Abstract base class for vision AI providers"""

    @abstractmethod
    def generate_alt_text(self, image_url: str, context: str | None = None) -> str:
        """Generate alt text for an image"""
        pass

    @abstractmethod
    def analyze_image_content(self, image_url: str) -> dict[str, Any]:
        """Analyze image content for accessibility and SEO"""
        pass


class GPTVisionProvider(VisionProvider):
    """OpenAI GPT-4o Vision provider"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")

        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4o"  # GPT-4o has vision capabilities

        logger.info("GPT-4o Vision provider initialized")

    def generate_alt_text(self, image_url: str, context: str | None = None) -> str:
        """Generate descriptive alt text using GPT-4o vision"""

        try:
            # Prepare the prompt
            system_prompt = """You are an expert at writing accessible alt text for images.
            Generate concise, descriptive alt text that:
            1. Describes the essential visual information
            2. Is under 125 characters for screen readers
            3. Focuses on content relevant to the context
            4. Avoids redundant phrases like "image of" or "picture showing"

            Return only the alt text, nothing else."""

            user_prompt = "Generate alt text for this image."
            if context:
                user_prompt += (
                    f" Context: This image appears in an article about {context}"
                )

            # Validate inputs for surrogates before API call
            validate_string_for_surrogates(
                system_prompt, "gpt_system_prompt", "generate_alt_text"
            )
            validate_string_for_surrogates(
                user_prompt, "gpt_user_prompt", "generate_alt_text"
            )
            validate_string_for_surrogates(image_url, "image_url", "generate_alt_text")

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url, "detail": "high"},
                            },
                        ],
                    },
                ],
                "max_tokens": 150,
                "temperature": 0.3,
            }

            # Pre-flight validation to prevent JSON corruption
            pre_flight_api_validation(payload, "gpt_vision_api")

            response = requests.post(
                self.base_url, headers=headers, json=payload, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                alt_text = result["choices"][0]["message"]["content"].strip()

                # Validate response doesn't contain surrogates
                validate_string_for_surrogates(
                    alt_text, "gpt_response", "generate_alt_text"
                )

                # Ensure alt text is within character limit
                if len(alt_text) > 125:
                    alt_text = alt_text[:122] + "..."

                logger.info(f"Generated alt text: {alt_text}")
                return alt_text
            else:
                logger.error(
                    f"GPT-4o API error: {response.status_code} - {response.text}"
                )
                return "Image content description unavailable"

        except Exception as e:
            logger.error(f"Error generating alt text with GPT-4o: {e}")
            return "Image description unavailable"

    def analyze_image_content(self, image_url: str) -> dict[str, Any]:
        """Analyze image for accessibility and content insights"""

        try:
            system_prompt = """Analyze this image for accessibility and content insights.
            Provide a JSON response with:
            - has_text: boolean (contains readable text)
            - content_type: string (photo, diagram, chart, screenshot, etc.)
            - accessibility_score: number 1-10 (how accessible without alt text)
            - key_elements: array of main visual elements
            - complexity: string (simple, moderate, complex)"""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this image:"},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url, "detail": "high"},
                            },
                        ],
                    },
                ],
                "max_tokens": 300,
                "temperature": 0.2,
            }

            response = requests.post(
                self.base_url, headers=headers, json=payload, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()

                # Try to parse JSON response
                try:
                    import json

                    analysis = json.loads(content)
                    return analysis
                except json.JSONDecodeError:
                    # Fallback analysis
                    return {
                        "has_text": False,
                        "content_type": "image",
                        "accessibility_score": 5,
                        "key_elements": ["visual content"],
                        "complexity": "moderate",
                    }
            else:
                logger.error(f"GPT-4o analysis error: {response.status_code}")
                return {"error": "Analysis unavailable"}

        except Exception as e:
            logger.error(f"Error analyzing image with GPT-4o: {e}")
            return {"error": str(e)}


class QwenVisionProvider(VisionProvider):
    """Qwen 2.5VL 7b local vision provider"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        self.model = "qwen2.5vl:7b"

        # Test connection
        try:
            test_url = f"{self.base_url}/api/tags"
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                logger.info("Qwen 2.5VL local model available")
            else:
                logger.warning("Qwen 2.5VL model may not be available")
        except Exception as e:
            logger.warning(f"Could not connect to local Qwen model: {e}")

    def generate_alt_text(self, image_url: str, context: str | None = None) -> str:
        """Generate alt text using local Qwen 2.5VL model"""

        try:
            prompt = """Generate concise alt text for this image. The alt text should:
            - Be under 125 characters
            - Describe essential visual information
            - Be accessible to screen readers
            - Not include phrases like "image of" or "picture showing"

            Return only the alt text."""

            if context:
                prompt += f"\n\nContext: This image appears in content about {context}"

            # Validate inputs for surrogates
            validate_string_for_surrogates(prompt, "qwen_prompt", "generate_alt_text")
            validate_string_for_surrogates(image_url, "image_url", "generate_alt_text")

            # Handle different image formats
            image_data = None
            if image_url.startswith("data:image/"):
                # Extract base64 data from data URL
                image_data = image_url.split(",")[1]
                # Validate base64 data
                validate_base64_string(image_data, "qwen_vision")
            elif image_url.startswith("http"):
                # For HTTP URLs, we'd need to fetch and convert to base64
                # For now, skip HTTP URLs as they need additional handling
                return "Remote images not yet supported in local model"
            else:
                # Assume it's already base64 data
                image_data = image_url
                validate_base64_string(image_data, "qwen_vision")

            # Prepare request for Ollama API
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_data] if image_data else [],
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 50},
            }

            # Pre-flight validation
            pre_flight_api_validation(payload, "qwen_vision_api")

            logger.info(f"Making request to: {self.base_url}/api/generate")
            logger.info(f"Payload model: {payload['model']}")
            logger.info(
                f"Image data length: {len(payload['images'][0]) if payload['images'] else 0}"
            )

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=45,  # Local model might be slower
            )

            logger.info(f"Response status: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"Response text: {response.text}")

            if response.status_code == 200:
                # Parse JSON response directly (stream=False returns single JSON)
                result = response.json()
                alt_text = result.get("response", "").strip()

                # Validate response doesn't contain surrogates
                validate_string_for_surrogates(
                    alt_text, "qwen_response", "generate_alt_text"
                )

                # Ensure character limit
                if len(alt_text) > 125:
                    alt_text = alt_text[:122] + "..."

                logger.info(f"Generated alt text (Qwen): {alt_text}")
                return alt_text if alt_text else "Image description unavailable"
            else:
                logger.error(f"Qwen API error: {response.status_code}")
                return "Image description unavailable"

        except Exception as e:
            logger.error(f"Error generating alt text with Qwen: {e}")
            return "Image description unavailable"

    def analyze_image_content(self, image_url: str) -> dict[str, Any]:
        """Analyze image content using Qwen 2.5VL"""

        try:
            prompt = """Analyze this image and provide insights in this exact JSON format:
            {
                "has_text": boolean,
                "content_type": "photo|diagram|chart|screenshot|graphic",
                "accessibility_score": number_1_to_10,
                "key_elements": ["element1", "element2"],
                "complexity": "simple|moderate|complex"
            }"""

            # Handle different image formats
            image_data = None
            if image_url.startswith("data:image/"):
                # Extract base64 data from data URL
                image_data = image_url.split(",")[1]
            elif image_url.startswith("http"):
                # For HTTP URLs, we'd need to fetch and convert to base64
                return {"error": "Remote images not yet supported in local model"}
            else:
                # Assume it's already base64 data
                image_data = image_url

            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_data] if image_data else [],
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 200},
            }

            response = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=45
            )

            if response.status_code == 200:
                # Parse JSON response directly (stream=False returns single JSON)
                result = response.json()
                content = result.get("response", "").strip()

                try:
                    import json

                    analysis = json.loads(content)
                    return analysis
                except json.JSONDecodeError:
                    return {
                        "has_text": False,
                        "content_type": "image",
                        "accessibility_score": 5,
                        "key_elements": ["visual content"],
                        "complexity": "moderate",
                    }
            else:
                return {"error": f"API error: {response.status_code}"}

        except Exception as e:
            logger.error(f"Error analyzing image with Qwen: {e}")
            return {"error": str(e)}


class VisionService:
    """Main vision service with provider selection"""

    def __init__(self, provider: str | None = None):
        self.provider_name = provider or os.getenv("VISION_PROVIDER", "openai")
        self.provider = None

        try:
            if self.provider_name.lower() == "openai":
                self.provider = GPTVisionProvider()
            elif self.provider_name.lower() in ["qwen", "local"]:
                self.provider = QwenVisionProvider()
            else:
                logger.warning(
                    f"Unknown vision provider: {self.provider_name}, defaulting to OpenAI"
                )
                self.provider = GPTVisionProvider()

        except Exception as e:
            logger.error(
                f"Failed to initialize vision provider {self.provider_name}: {e}"
            )
            # Try fallback provider
            try:
                if self.provider_name != "openai":
                    logger.info("Attempting OpenAI as fallback")
                    self.provider = GPTVisionProvider()
                else:
                    logger.info("Attempting Qwen as fallback")
                    self.provider = QwenVisionProvider()
            except Exception as fallback_error:
                logger.error(f"Fallback provider also failed: {fallback_error}")
                self.provider = None

    def generate_alt_text(self, image_url: str, context: str | None = None) -> str:
        """Generate alt text for image URL"""
        if not self.provider:
            return "Vision service unavailable"

        return self.provider.generate_alt_text(image_url, context)

    def analyze_image(self, image_url: str) -> dict[str, Any]:
        """Analyze image content"""
        if not self.provider:
            return {"error": "Vision service unavailable"}

        return self.provider.analyze_image_content(image_url)

    def is_available(self) -> bool:
        """Check if vision service is available"""
        return self.provider is not None

    def get_provider_name(self) -> str:
        """Get current provider name"""
        return self.provider_name
