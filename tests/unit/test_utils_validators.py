"""Tests for validator and utility functions in core/utils.py."""

import pytest

from unraid_mcp.core.exceptions import ValidationError
from unraid_mcp.core.utils import (
    truncate_for_error,
    validate_enum,
    validate_log_file_path,
    validate_positive_int,
    validate_string_not_empty,
)


class TestValidatePositiveInt:
    def test_valid_value(self):
        assert validate_positive_int(5, "count") == 5

    def test_zero_passes(self):
        assert validate_positive_int(0, "offset") == 0

    def test_negative_raises(self):
        with pytest.raises(ValidationError, match="non-negative"):
            validate_positive_int(-1, "count")

    def test_exceeds_max_raises(self):
        with pytest.raises(ValidationError, match="at most 100"):
            validate_positive_int(101, "limit", max_value=100)

    def test_no_max(self):
        assert validate_positive_int(999999, "big") == 999999


class TestValidateEnum:
    def test_valid_value(self):
        assert validate_enum("start", ["start", "stop"], "action") == "start"

    def test_invalid_raises(self):
        with pytest.raises(ValidationError, match="Invalid action"):
            validate_enum("restart", ["start", "stop"], "action")


class TestValidateStringNotEmpty:
    def test_valid_string(self):
        assert validate_string_not_empty("hello", "name") == "hello"

    def test_empty_raises(self):
        with pytest.raises(ValidationError, match="must not be empty"):
            validate_string_not_empty("", "name")

    def test_whitespace_raises(self):
        with pytest.raises(ValidationError, match="must not be empty"):
            validate_string_not_empty("   ", "name")


class TestValidateLogFilePath:
    def test_valid_path(self):
        assert validate_log_file_path("/var/log/syslog") == "/var/log/syslog"

    def test_empty_raises(self):
        with pytest.raises(ValidationError, match="must not be empty"):
            validate_log_file_path("")

    def test_null_byte_raises(self):
        with pytest.raises(ValidationError, match="null bytes"):
            validate_log_file_path("/var/log/\x00evil")

    def test_traversal_raises(self):
        with pytest.raises(ValidationError, match="must not contain"):
            validate_log_file_path("/var/log/../etc/passwd")

    def test_relative_path_raises(self):
        with pytest.raises(ValidationError, match="absolute path"):
            validate_log_file_path("relative/path")

    @pytest.mark.parametrize(
        "path",
        [
            "/var/log/syslog",
            "/boot/logs/mylog.txt",
            "/boot/config/some.cfg",
            "/mnt/user/share/file.log",
            "/tmp/debug.log",
        ],
    )
    def test_allowed_prefixes(self, path: str):
        assert validate_log_file_path(path) == path

    def test_disallowed_prefix_raises(self):
        with pytest.raises(ValidationError, match="must start with one of"):
            validate_log_file_path("/etc/passwd")

    def test_disallowed_root_raises(self):
        with pytest.raises(ValidationError, match="must start with one of"):
            validate_log_file_path("/home/user/file")


class TestTruncateForError:
    def test_short_unchanged(self):
        assert truncate_for_error("hello") == "hello"

    def test_long_truncated(self):
        long_text = "x" * 600
        result = truncate_for_error(long_text)
        assert len(result) < 600
        assert "truncated" in result
        assert "600 chars" in result

    def test_at_limit_boundary(self):
        text = "x" * 500
        assert truncate_for_error(text) == text

    def test_custom_max_length(self):
        text = "x" * 20
        result = truncate_for_error(text, max_length=10)
        assert "truncated" in result
