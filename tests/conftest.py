import sys
from pathlib import Path

import pytest


def pytest_configure(config):
    """Add project root to sys.path so tests can import the package."""
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_graphql_response():
    """Factory for mock GraphQL responses."""

    def _make(data=None, errors=None):
        resp = {}
        if data is not None:
            resp["data"] = data
        if errors is not None:
            resp["errors"] = errors
        return resp

    return _make
