"""Tests for Docker helper functions (pure functions, no mocking needed)."""

from unraid_mcp.tools.docker import (
    _is_container_id,
    find_container_by_identifier,
    get_available_container_names,
)


class TestIsContainerId:
    def test_64_char_hex(self):
        assert _is_container_id("a" * 64) is True

    def test_12_char_hex(self):
        assert _is_container_id("abcdef123456") is True

    def test_colon_prefixed(self):
        assert _is_container_id("sha256:abc123") is True

    def test_regular_name_false(self):
        assert _is_container_id("my-container") is False

    def test_too_short_hex(self):
        assert _is_container_id("abcdef") is False

    def test_non_hex_chars(self):
        assert _is_container_id("ghijklmnopqr") is False


class TestFindContainerByIdentifier:
    CONTAINERS = [
        {"id": "sha256:abc123", "names": ["plex"]},
        {"id": "sha256:def456", "names": ["nginx", "web-server"]},
        {"id": "sha256:ghi789", "names": ["homeassistant"]},
    ]

    def test_exact_id_match(self):
        result = find_container_by_identifier("sha256:abc123", self.CONTAINERS)
        assert result is not None
        assert result["names"] == ["plex"]

    def test_exact_name_match(self):
        result = find_container_by_identifier("nginx", self.CONTAINERS)
        assert result is not None
        assert result["id"] == "sha256:def456"

    def test_case_insensitive_partial(self):
        result = find_container_by_identifier("PLEX", self.CONTAINERS)
        assert result is not None
        assert result["names"] == ["plex"]

    def test_not_found_returns_none(self):
        result = find_container_by_identifier("nonexistent", self.CONTAINERS)
        assert result is None

    def test_empty_list_returns_none(self):
        result = find_container_by_identifier("plex", [])
        assert result is None


class TestGetAvailableContainerNames:
    def test_extracts_names(self):
        containers = [
            {"names": ["plex"]},
            {"names": ["nginx", "web"]},
        ]
        names = get_available_container_names(containers)
        assert names == ["plex", "nginx", "web"]

    def test_empty_list(self):
        assert get_available_container_names([]) == []

    def test_missing_names_field(self):
        containers = [{"id": "abc"}, {"names": ["nginx"]}]
        names = get_available_container_names(containers)
        assert names == ["nginx"]
