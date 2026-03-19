import unittest

from unraid_mcp.core.utils import ensure_dict, ensure_list, format_bytes, format_kb

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
        self.assertEqual(format_kb(512), "512 KB")

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


if __name__ == "__main__":
    unittest.main()
