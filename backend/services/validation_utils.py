"""
Validation utilities to prevent UTF-16 surrogate corruption in API requests.

This module provides safeguards against the specific issue where unpaired UTF-16
surrogates in strings cause JSON serialization failures in API calls.
"""

import base64
import json
import re
from pathlib import Path
from typing import Any

# Regex patterns for detecting unpaired UTF-16 surrogates
UNPAIRED_HIGH_SURROGATE = re.compile(r"[\uD800-\uDBFF](?![\uDC00-\uDFFF])")
UNPAIRED_LOW_SURROGATE = re.compile(r"(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]")


class SurrogateValidationError(Exception):
    """Raised when unpaired UTF-16 surrogates are detected in data."""

    def __init__(self, json_path: str, sample: str, source: str = "unknown"):
        self.json_path = json_path
        self.sample = sample
        self.source = source
        super().__init__(
            f"Unpaired UTF-16 surrogate at {json_path}: {sample[:40]}... (source: {source})"
        )


def validate_string_for_surrogates(
    text: str, json_path: str = "", source: str = "unknown"
) -> None:
    """
    Validate a string for unpaired UTF-16 surrogates.

    Args:
        text: String to validate
        json_path: JSON path for error reporting (e.g., "$.messages[2].content")
        source: Source that produced this string (e.g., "vision_service", "base64_decode")

    Raises:
        SurrogateValidationError: If unpaired surrogates are found
    """
    if UNPAIRED_HIGH_SURROGATE.search(text) or UNPAIRED_LOW_SURROGATE.search(text):
        # Get sample of problematic text, escaped for safety
        sample = repr(text[:40])
        raise SurrogateValidationError(json_path, sample, source)


def validate_object_for_surrogates(
    obj: Any, path: str = "$", source: str = "unknown"
) -> None:
    """
    Recursively validate an object for unpaired UTF-16 surrogates.

    Args:
        obj: Object to validate (dict, list, str, or primitive)
        path: Current JSON path for error reporting
        source: Source that produced this object

    Raises:
        SurrogateValidationError: If unpaired surrogates are found
    """
    if isinstance(obj, str):
        validate_string_for_surrogates(obj, path, source)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            # Validate the key itself
            validate_string_for_surrogates(str(key), f"{path}.{key}[key]", source)
            # Validate the value
            validate_object_for_surrogates(value, f"{path}.{key}", source)
    elif isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj):
            validate_object_for_surrogates(item, f"{path}[{i}]", source)
    # Primitives (int, float, bool, None) are safe


def safe_json_dumps(obj: Any, source: str = "unknown", **kwargs) -> str:
    """
    JSON serialize with pre-flight surrogate validation.

    Args:
        obj: Object to serialize
        source: Source identifier for error reporting
        **kwargs: Additional arguments passed to json.dumps

    Returns:
        JSON string

    Raises:
        SurrogateValidationError: If unpaired surrogates detected before serialization
    """
    # Pre-flight validation
    validate_object_for_surrogates(obj, "$", source)

    # Safe to serialize
    return json.dumps(obj, **kwargs)


def validate_base64_string(b64_string: str, source: str = "unknown") -> bytes:
    """
    Validate and decode a base64 string, ensuring clean UTF-16 handling.

    Args:
        b64_string: Base64 encoded string
        source: Source identifier for error reporting

    Returns:
        Decoded bytes

    Raises:
        ValueError: If base64 is invalid
        SurrogateValidationError: If the base64 string itself contains surrogates
    """
    # First validate the base64 string itself doesn't contain surrogates
    validate_string_for_surrogates(b64_string, "base64_input", source)

    # Strip data URL prefix if present
    if b64_string.startswith("data:"):
        if ";base64," in b64_string:
            b64_string = b64_string.split(";base64,", 1)[1]

    # Remove whitespace
    b64_string = re.sub(r"\s+", "", b64_string)

    # Strict decode with validation
    try:
        decoded_bytes = base64.b64decode(b64_string, validate=True)
    except Exception as e:
        raise ValueError(f"Invalid base64 from {source}: {e}")

    return decoded_bytes


def write_binary_to_temp_file(
    data: bytes, prefix: str = "vision_", suffix: str = ".bin"
) -> Path:
    """
    Write binary data to a temporary file, avoiding string contamination.

    Args:
        data: Binary data to write
        prefix: Filename prefix
        suffix: Filename suffix/extension

    Returns:
        Path to the temporary file
    """
    import os
    import tempfile

    # Create temp file
    fd, temp_path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
    temp_file = Path(temp_path)

    try:
        # Write binary data directly using the file descriptor
        os.write(fd, data)
    finally:
        # Close the file descriptor
        os.close(fd)

    return temp_file


def create_safe_image_reference(
    image_data: bytes, filename_hint: str = "image"
) -> dict[str, Any]:
    """
    Create a safe image reference for API calls, avoiding base64 embedding.

    Args:
        image_data: Raw image bytes
        filename_hint: Hint for filename (will be sanitized)

    Returns:
        Dictionary with safe image reference (file path, not embedded data)
    """
    # Sanitize filename
    safe_filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename_hint)

    # Determine extension from data
    if image_data.startswith(b"\x89PNG"):
        suffix = ".png"
    elif image_data.startswith(b"\xff\xd8\xff"):
        suffix = ".jpg"
    elif image_data.startswith(b"RIFF") and b"WEBP" in image_data[:12]:
        suffix = ".webp"
    else:
        suffix = ".bin"

    # Write to temp file
    temp_file = write_binary_to_temp_file(image_data, f"img_{safe_filename}_", suffix)

    return {
        "type": "image_file",
        "file_path": str(temp_file),
        "size_bytes": len(image_data),
        "format": suffix[1:],  # Remove the dot
    }


def pre_flight_api_validation(
    payload: dict[str, Any], source: str = "api_request"
) -> None:
    """
    Pre-flight validation before any API call to prevent surrogate corruption.

    This should be called before every model API request or external service call.

    Args:
        payload: The complete request payload
        source: Identifier for where this payload originated

    Raises:
        SurrogateValidationError: If validation fails
    """
    validate_object_for_surrogates(payload, "$", source)

    # Additional checks for common problematic patterns
    if isinstance(payload, dict):
        messages = payload.get("messages", [])
        if isinstance(messages, list):
            for i, msg in enumerate(messages):
                if isinstance(msg, dict):
                    content = msg.get("content", "")
                    if isinstance(content, str) and len(content) > 10000:
                        # Large content strings are suspicious for base64 embedding
                        if "data:" in content or content.count("=") > 100:
                            raise SurrogateValidationError(
                                f"$.messages[{i}].content",
                                "Suspected base64 embedding (file-first required)",
                                source,
                            )


# Convenience decorator for API functions
def validate_surrogates(source: str = "decorated_function"):
    """
    Decorator to automatically validate function arguments for surrogates.

    Args:
        source: Source identifier for error reporting
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Validate all arguments
            for i, arg in enumerate(args):
                validate_object_for_surrogates(
                    arg, f"args[{i}]", f"{source}.{func.__name__}"
                )

            for key, value in kwargs.items():
                validate_object_for_surrogates(
                    value, f"kwargs.{key}", f"{source}.{func.__name__}"
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator
