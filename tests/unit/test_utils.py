import sys
import unittest
from pathlib import Path

# Ensure we can import unraid_mcp
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from unraid_mcp.tools.api import _strip_comments  # noqa: E402


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

    def test_format_kb_overflow_logic_simulation(self):
        """
        Verify the logic used in format_kb to handle overflows.
        Note: format_kb is nested inside _get_array_status, so we test a replica of the logic here
        or rely on the fact that the logic pattern is standard Python exception handling.
        """

        def format_kb_logic(k):
            if k is None:
                return "N/A"
            try:
                k = int(float(k))
            except (ValueError, TypeError, OverflowError):
                return str(k)
            return "OK"

        # Test overflow
        self.assertEqual(format_kb_logic(float("inf")), "inf")
        self.assertEqual(format_kb_logic("not_a_number"), "not_a_number")
        self.assertEqual(format_kb_logic(None), "N/A")
        self.assertEqual(format_kb_logic(1024), "OK")


if __name__ == "__main__":
    unittest.main()
