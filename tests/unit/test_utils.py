import unittest

import pytest

from unraid_mcp.core.utils import (
    ensure_dict,
    ensure_list,
    format_bytes,
    format_kb,
    poll_with_backoff,
)

# unraid_mcp.tools.api is now importable thanks to conftest.py or pip install -e .
from unraid_mcp.tools.api import _strip_comments


class TestUtils(unittest.TestCase):
    def test_strip_comments(self):
        # Basic comment stripping
        query = """
        query {
            field # This is a comment
            anotherField
        }
        """
        stripped = _strip_comments(query)
        self.assertNotIn("# This is a comment", stripped)
        self.assertIn("field", stripped)

        # String preservation
        query_str = 'field(arg: "some # string")'
        stripped_str = _strip_comments(query_str)
        self.assertIn('""', stripped_str)  # It replaces strings with ""

        # Block string
        query_block = 'field(arg: """block # string""")'
        stripped_block = _strip_comments(query_block)
        self.assertIn('""""""', stripped_block)  # It replaces block strings

    def test_format_kb(self):
        """
        Verify the logic of the real format_kb function directly.
        """
        # Test overflow/special cases
        self.assertEqual(format_kb(float("inf")), "inf")
        self.assertEqual(format_kb("not_a_number"), "not_a_number")
        self.assertEqual(format_kb(None), "N/A")

        # Test formatting
        self.assertEqual(format_kb(1024), "1.00 MB")
        self.assertEqual(format_kb(1024 * 1024), "1.00 GB")
        self.assertEqual(format_kb(512), "512.00 KB")

    def test_ensure_dict(self):
        self.assertEqual(ensure_dict({"a": 1}), {"a": 1})
        self.assertEqual(ensure_dict(None), {})
        self.assertEqual(ensure_dict([1, 2]), {})
        self.assertEqual(ensure_dict("string"), {})
        self.assertEqual(ensure_dict(42), {})

    def test_ensure_list(self):
        self.assertEqual(ensure_list([1, 2, 3]), [1, 2, 3])
        self.assertEqual(ensure_list(None), [])
        self.assertEqual(ensure_list({"a": 1}), [])
        self.assertEqual(ensure_list("string"), [])
        self.assertEqual(ensure_list(42), [])

    def test_format_bytes(self):
        self.assertEqual(format_bytes(None), "N/A")
        self.assertEqual(format_bytes(0), "0.00 B")
        self.assertEqual(format_bytes(1024), "1.00 KB")
        self.assertEqual(format_bytes(1024 * 1024), "1.00 MB")
        self.assertEqual(format_bytes(1024 * 1024 * 1024), "1.00 GB")
        self.assertEqual(format_bytes(1024**4), "1.00 TB")
        self.assertEqual(format_bytes(1024**5), "1.00 PB")
        self.assertEqual(format_bytes(1024**6), "1.00 EB")
        self.assertEqual(format_bytes(500), "500.00 B")


class TestPollWithBackoff:
    @pytest.mark.asyncio
    async def test_returns_first_non_none(self):
        call_count = 0

        async def query():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                return {"found": True}
            return None

        result = await poll_with_backoff(
            query_fn=query,
            max_retries=5,
            initial_delay=0.01,
            backoff_factor=1.0,
            operation_name="test",
        )
        assert result == {"found": True}
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_returns_none_after_max_retries(self):
        call_count = 0

        async def query():
            nonlocal call_count
            call_count += 1
            return None

        result = await poll_with_backoff(
            query_fn=query,
            max_retries=3,
            initial_delay=0.01,
            backoff_factor=1.0,
            operation_name="test",
        )
        assert result is None
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_returns_immediately_on_first_success(self):
        async def query():
            return "immediate"

        result = await poll_with_backoff(
            query_fn=query,
            max_retries=5,
            initial_delay=0.01,
            backoff_factor=1.0,
        )
        assert result == "immediate"

    @pytest.mark.asyncio
    async def test_handles_exceptions_gracefully(self):
        call_count = 0

        async def query():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("transient error")
            return "recovered"

        result = await poll_with_backoff(
            query_fn=query,
            max_retries=5,
            initial_delay=0.01,
            backoff_factor=1.0,
            operation_name="test",
        )
        assert result == "recovered"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_returns_none_when_all_attempts_raise(self):
        async def query():
            raise RuntimeError("persistent error")

        result = await poll_with_backoff(
            query_fn=query,
            max_retries=3,
            initial_delay=0.01,
            backoff_factor=1.0,
            operation_name="test",
        )
        assert result is None


class TestSafeDisplayUrl:
    def test_strips_path(self):
        from unraid_mcp.core.utils import safe_display_url
        assert safe_display_url("https://192.168.1.101:8443/graphql") == "https://192.168.1.101:8443"

    def test_strips_query(self):
        from unraid_mcp.core.utils import safe_display_url
        assert safe_display_url("https://host:443/path?key=secret") == "https://host:443"

    def test_strips_credentials(self):
        from unraid_mcp.core.utils import safe_display_url
        assert safe_display_url("https://user:pass@host:443/path") == "https://host:443"

    def test_preserves_scheme_and_host(self):
        from unraid_mcp.core.utils import safe_display_url
        assert safe_display_url("http://myserver:6970") == "http://myserver:6970"

    def test_no_port(self):
        from unraid_mcp.core.utils import safe_display_url
        assert safe_display_url("https://myserver/graphql") == "https://myserver"

    def test_invalid_url_returns_placeholder(self):
        from unraid_mcp.core.utils import safe_display_url
        assert safe_display_url("not a url at all") == "<invalid-url>"

    def test_empty_string(self):
        from unraid_mcp.core.utils import safe_display_url
        assert safe_display_url("") == "<invalid-url>"


if __name__ == "__main__":
    unittest.main()
