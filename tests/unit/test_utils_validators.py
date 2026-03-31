"""Tests for validator and utility functions in core/validation.py."""

import pytest

from unraid_mcp.core.exceptions import ValidationError
from unraid_mcp.core.validation import (
    DANGEROUS_KEY_PATTERN,
    MAX_VALUE_LENGTH,
    truncate_for_error,
    validate_enum,
    validate_log_file_path,
    validate_path,
    validate_positive_int,
    validate_rclone_remote_name,
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
        with pytest.raises(ValidationError, match="traversal|must start with"):
            validate_log_file_path("/var/log/../etc/passwd")

    def test_relative_path_raises(self):
        with pytest.raises(ValidationError, match="absolute path|must start with"):
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


class TestValidateRcloneRemoteName:
    def test_valid_simple(self):
        assert validate_rclone_remote_name("myremote") == "myremote"

    def test_valid_with_hyphens_underscores(self):
        assert validate_rclone_remote_name("my-remote_1") == "my-remote_1"

    def test_valid_single_char(self):
        assert validate_rclone_remote_name("a") == "a"

    def test_valid_max_length(self):
        name = "a" * 64
        assert validate_rclone_remote_name(name) == name

    def test_empty_raises(self):
        with pytest.raises(ValidationError, match="must not be empty"):
            validate_rclone_remote_name("")

    def test_starts_with_hyphen_raises(self):
        with pytest.raises(ValidationError, match="Invalid remote name"):
            validate_rclone_remote_name("-bad")

    def test_contains_colon_raises(self):
        with pytest.raises(ValidationError, match="Invalid remote name"):
            validate_rclone_remote_name("my:remote")

    def test_contains_space_raises(self):
        with pytest.raises(ValidationError, match="Invalid remote name"):
            validate_rclone_remote_name("my remote")

    def test_too_long_raises(self):
        with pytest.raises(ValidationError, match="Invalid remote name"):
            validate_rclone_remote_name("a" * 65)

    def test_path_traversal_raises(self):
        with pytest.raises(ValidationError, match="Invalid remote name"):
            validate_rclone_remote_name("../etc/passwd")


class TestValidatePath:
    def test_valid_path_passes(self):
        result = validate_path("/var/log/syslog", ["/var/log"], "my_path")
        assert result == "/var/log/syslog"

    def test_valid_nested_path_passes(self):
        result = validate_path("/var/log/app/server.log", ["/var/log"], "my_path")
        assert result == "/var/log/app/server.log"

    def test_rejects_null_bytes(self):
        with pytest.raises(ValidationError, match="null bytes"):
            validate_path("/var/log/\x00evil", ["/var/log"], "my_path")

    def test_rejects_traversal(self):
        with pytest.raises(ValidationError, match="traversal"):
            validate_path("../../etc/shadow", ["/var/log"], "my_path")

    def test_rejects_encoded_traversal(self):
        with pytest.raises(ValidationError, match="traversal|allowed|must start with"):
            validate_path("/var/log/foo/../../../etc/passwd", ["/var/log"], "my_path")

    def test_rejects_path_outside_allowed_prefixes(self):
        with pytest.raises(ValidationError, match="must start with one of"):
            validate_path("/etc/passwd", ["/var/log"], "my_path")

    def test_multiple_allowed_prefixes(self):
        result = validate_path("/boot/logs/mylog.txt", ["/var/log", "/boot/logs"], "my_path")
        assert result == "/boot/logs/mylog.txt"

    def test_normpath_resolves_dot_components(self):
        result = validate_path("/var/log/./app/server.log", ["/var/log"], "my_path")
        assert result == "/var/log/app/server.log"

    def test_empty_path_raises(self):
        with pytest.raises(ValidationError):
            validate_path("", ["/var/log"], "my_path")


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


class TestDangerousKeyPattern:
    def test_rejects_path_traversal(self):
        assert DANGEROUS_KEY_PATTERN.search("..") is not None

    def test_rejects_forward_slash(self):
        assert DANGEROUS_KEY_PATTERN.search("foo/bar") is not None

    def test_rejects_backslash(self):
        assert DANGEROUS_KEY_PATTERN.search("foo\\bar") is not None

    def test_rejects_shell_pipe(self):
        assert DANGEROUS_KEY_PATTERN.search("foo|bar") is not None

    def test_rejects_semicolon(self):
        assert DANGEROUS_KEY_PATTERN.search("foo;bar") is not None

    def test_rejects_dollar(self):
        assert DANGEROUS_KEY_PATTERN.search("foo$bar") is not None

    def test_rejects_backtick(self):
        assert DANGEROUS_KEY_PATTERN.search("foo`bar") is not None

    def test_rejects_null_byte(self):
        assert DANGEROUS_KEY_PATTERN.search("foo\x00bar") is not None

    def test_rejects_control_char(self):
        assert DANGEROUS_KEY_PATTERN.search("foo\x01bar") is not None

    def test_rejects_space(self):
        assert DANGEROUS_KEY_PATTERN.search("foo bar") is not None

    def test_allows_clean_key(self):
        assert DANGEROUS_KEY_PATTERN.search("my_remote_name") is None

    def test_allows_hyphen_underscore(self):
        assert DANGEROUS_KEY_PATTERN.search("my-remote_name-123") is None

    def test_max_value_length(self):
        assert MAX_VALUE_LENGTH == 4096
