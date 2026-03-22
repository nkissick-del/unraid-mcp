"""Tests for Docker batch operation tools."""

import pytest

from unraid_mcp.core.exceptions import ValidationError
from unraid_mcp.core.utils import validate_string_not_empty
from unraid_mcp.tools.queries.docker_batch import (
    DOCKER_UPDATE_ALL_CONTAINERS_MUTATION,
    DOCKER_UPDATE_AUTOSTART_MUTATION,
    DOCKER_UPDATE_CONTAINERS_MUTATION,
)


class TestDockerBatchMutationStrings:
    @pytest.mark.parametrize(
        "mutation,keywords",
        [
            (
                DOCKER_UPDATE_CONTAINERS_MUTATION,
                ["mutation", "$ids", "PrefixedID", "docker", "id", "names", "state", "image"],
            ),
            (
                DOCKER_UPDATE_ALL_CONTAINERS_MUTATION,
                ["mutation", "updateAllContainers", "docker", "id", "names", "state", "image"],
            ),
            (
                DOCKER_UPDATE_AUTOSTART_MUTATION,
                ["mutation", "$input", "AutostartConfigurationInput", "docker", "autoStart"],
            ),
        ],
    )
    def test_mutation_structure(self, mutation, keywords):
        for kw in keywords:
            assert kw in mutation


class TestDockerBatchValidation:
    def test_empty_container_id_raises(self):
        with pytest.raises(ValidationError):
            validate_string_not_empty("", "container_id")

    def test_whitespace_container_id_raises(self):
        with pytest.raises(ValidationError):
            validate_string_not_empty("   ", "container_id")
