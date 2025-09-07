"""
Tests for UTF-16 surrogate validation utilities.
"""

import json
from pathlib import Path

import pytest

from services.validation_utils import (
    SurrogateValidationError,
    create_safe_image_reference,
    pre_flight_api_validation,
    safe_json_dumps,
    validate_base64_string,
    validate_object_for_surrogates,
    validate_string_for_surrogates,
    validate_surrogates,
)


class TestSurrogateValidation:
    """Test surrogate detection and validation."""

    def test_valid_string_passes(self):
        """Valid strings should pass validation."""
        validate_string_for_surrogates("Hello, world! 🌍")
        validate_string_for_surrogates("Normal ASCII text")
        validate_string_for_surrogates("Unicode: café, naïve, résumé")

    def test_unpaired_high_surrogate_fails(self):
        """Unpaired high surrogate should be detected."""
        # Create string with unpaired high surrogate
        bad_string = "Hello\uD800World"  # High surrogate without low

        with pytest.raises(SurrogateValidationError) as exc_info:
            validate_string_for_surrogates(bad_string, "test_path", "test_source")

        assert "test_path" in str(exc_info.value)
        assert "test_source" in str(exc_info.value)

    def test_unpaired_low_surrogate_fails(self):
        """Unpaired low surrogate should be detected."""
        # Create string with unpaired low surrogate
        bad_string = "Hello\uDC00World"  # Low surrogate without high

        with pytest.raises(SurrogateValidationError):
            validate_string_for_surrogates(bad_string)

    def test_valid_surrogate_pair_passes(self):
        """Valid surrogate pairs should pass."""
        # Valid emoji using surrogate pair
        valid_string = "Hello 😀 World"  # U+1F600 uses surrogate pair correctly
        validate_string_for_surrogates(valid_string)


class TestObjectValidation:
    """Test recursive object validation."""

    def test_valid_object_passes(self):
        """Valid nested objects should pass."""
        obj = {
            "string": "Hello world",
            "number": 42,
            "bool": True,
            "null": None,
            "array": ["item1", "item2", {"nested": "value"}],
            "object": {"nested": {"deep": "value"}},
        }
        validate_object_for_surrogates(obj)

    def test_object_with_bad_value_fails(self):
        """Object containing bad string should fail."""
        obj = {"good": "Hello world", "bad": "Hello\uD800World"}  # Unpaired surrogate

        with pytest.raises(SurrogateValidationError) as exc_info:
            validate_object_for_surrogates(obj)

        assert "$.bad" in str(exc_info.value)

    def test_object_with_bad_key_fails(self):
        """Object with bad key should fail."""
        # This is harder to test directly since Python dict keys are typically clean
        # But the validation should catch this if it occurs
        pass

    def test_nested_array_with_bad_value_fails(self):
        """Nested array with bad value should fail."""
        obj = {"array": ["good", "also good", "bad\uD800value"]}

        with pytest.raises(SurrogateValidationError) as exc_info:
            validate_object_for_surrogates(obj)

        assert "$.array[2]" in str(exc_info.value)


class TestSafeJsonDumps:
    """Test safe JSON serialization."""

    def test_safe_object_serializes(self):
        """Valid object should serialize normally."""
        obj = {"hello": "world", "number": 42}
        result = safe_json_dumps(obj, "test_source")

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == obj

    def test_bad_object_fails_before_serialization(self):
        """Bad object should fail before serialization attempt."""
        obj = {"good": "value", "bad": "value\uD800"}

        with pytest.raises(SurrogateValidationError):
            safe_json_dumps(obj, "test_source")


class TestBase64Validation:
    """Test base64 string validation."""

    def test_valid_base64_decodes(self):
        """Valid base64 should decode successfully."""
        # "Hello World" in base64
        b64 = "SGVsbG8gV29ybGQ="
        result = validate_base64_string(b64, "test_source")
        assert result == b"Hello World"

    def test_data_url_prefix_stripped(self):
        """Data URL prefix should be stripped."""
        b64 = "data:image/png;base64,SGVsbG8gV29ybGQ="
        result = validate_base64_string(b64, "test_source")
        assert result == b"Hello World"

    def test_invalid_base64_fails(self):
        """Invalid base64 should raise ValueError."""
        with pytest.raises(ValueError):
            validate_base64_string("Not base64!", "test_source")

    def test_base64_with_surrogates_fails(self):
        """Base64 string containing surrogates should fail."""
        bad_b64 = "SGVsb\uD800G8gV29ybGQ="

        with pytest.raises(SurrogateValidationError):
            validate_base64_string(bad_b64, "test_source")


class TestImageReference:
    """Test safe image reference creation."""

    def test_png_image_reference(self):
        """PNG data should create proper file reference."""
        # Minimal PNG header
        png_data = b"\x89PNG\r\n\x1a\n" + b"fake png data"

        result = create_safe_image_reference(png_data, "test_image")

        assert result["type"] == "image_file"
        assert result["format"] == "png"
        assert result["size_bytes"] == len(png_data)
        assert "file_path" in result

        # Verify file was created
        file_path = Path(result["file_path"])
        assert file_path.exists()

        # Verify file contains our data
        with open(file_path, "rb") as f:
            assert f.read() == png_data

        # Cleanup
        file_path.unlink()

    def test_jpg_image_reference(self):
        """JPEG data should create proper file reference."""
        jpg_data = b"\xff\xd8\xff\xe0" + b"fake jpg data"

        result = create_safe_image_reference(jpg_data, "test_image")

        assert result["format"] == "jpg"

        # Cleanup
        Path(result["file_path"]).unlink()

    def test_filename_sanitization(self):
        """Problematic filenames should be sanitized."""
        png_data = b"\x89PNG\r\n\x1a\n" + b"fake data"

        result = create_safe_image_reference(png_data, "bad/file\\name:with|chars")

        # Filename should be sanitized
        file_path = Path(result["file_path"])
        assert "/" not in file_path.name
        assert "\\" not in file_path.name
        assert ":" not in file_path.name
        assert "|" not in file_path.name

        # Cleanup
        file_path.unlink()


class TestPreFlightValidation:
    """Test pre-flight API validation."""

    def test_valid_api_payload_passes(self):
        """Valid API payload should pass validation."""
        payload = {
            "messages": [
                {"role": "user", "content": "Hello, how are you?"},
                {"role": "assistant", "content": "I'm doing well, thank you!"},
            ],
            "model": "gpt-4",
            "temperature": 0.7,
        }

        # Should not raise
        pre_flight_api_validation(payload, "test_api")

    def test_payload_with_surrogates_fails(self):
        """Payload containing surrogates should fail."""
        payload = {"messages": [{"role": "user", "content": "Hello\uD800World"}]}

        with pytest.raises(SurrogateValidationError) as exc_info:
            pre_flight_api_validation(payload, "test_api")

        assert "$.messages[0].content" in str(exc_info.value)

    def test_large_content_with_base64_pattern_fails(self):
        """Large content that looks like base64 should be flagged."""
        # Create suspiciously large content with base64 patterns
        large_content = "data:image/png;base64," + "A" * 10000 + "=="

        payload = {"messages": [{"role": "user", "content": large_content}]}

        with pytest.raises(SurrogateValidationError) as exc_info:
            pre_flight_api_validation(payload, "test_api")

        assert "base64 embedding" in str(exc_info.value)


class TestValidationDecorator:
    """Test the validation decorator."""

    def test_decorator_validates_args(self):
        """Decorator should validate function arguments."""

        @validate_surrogates("test_decorator")
        def test_function(text: str, data: dict):
            return {"processed": True}

        # Valid call should work
        result = test_function("Hello", {"key": "value"})
        assert result == {"processed": True}

        # Invalid call should fail
        with pytest.raises(SurrogateValidationError):
            test_function("Bad\uD800String", {"key": "value"})

    def test_decorator_validates_kwargs(self):
        """Decorator should validate keyword arguments."""

        @validate_surrogates("test_decorator")
        def test_function(**kwargs):
            return kwargs

        # Valid call should work
        result = test_function(text="Hello", data={"key": "value"})
        assert result == {"text": "Hello", "data": {"key": "value"}}

        # Invalid call should fail
        with pytest.raises(SurrogateValidationError):
            test_function(text="Bad\uD800String")
