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
    def test_update_containers_has_ids_variable(self):
        assert "$ids" in DOCKER_UPDATE_CONTAINERS_MUTATION
        assert "PrefixedID" in DOCKER_UPDATE_CONTAINERS_MUTATION

    def test_update_all_containers_is_valid_graphql(self):
        assert "mutation" in DOCKER_UPDATE_ALL_CONTAINERS_MUTATION
        assert "updateAllContainers" in DOCKER_UPDATE_ALL_CONTAINERS_MUTATION

    def test_update_autostart_has_input_variable(self):
        assert "$input" in DOCKER_UPDATE_AUTOSTART_MUTATION
        assert "AutostartConfigurationInput" in DOCKER_UPDATE_AUTOSTART_MUTATION

    def test_all_mutations_contain_container_fields(self):
        for mutation in [
            DOCKER_UPDATE_CONTAINERS_MUTATION,
            DOCKER_UPDATE_ALL_CONTAINERS_MUTATION,
        ]:
            assert "id" in mutation
            assert "names" in mutation
            assert "state" in mutation
            assert "image" in mutation

    def test_autostart_mutation_returns_autostart_field(self):
        assert "autoStart" in DOCKER_UPDATE_AUTOSTART_MUTATION

    def test_all_mutations_nested_under_docker(self):
        for mutation in [
            DOCKER_UPDATE_CONTAINERS_MUTATION,
            DOCKER_UPDATE_ALL_CONTAINERS_MUTATION,
            DOCKER_UPDATE_AUTOSTART_MUTATION,
        ]:
            assert "docker" in mutation


class TestDockerBatchValidation:
    def test_empty_container_id_raises(self):
        with pytest.raises(ValidationError):
            validate_string_not_empty("", "container_id")

    def test_whitespace_container_id_raises(self):
        with pytest.raises(ValidationError):
            validate_string_not_empty("   ", "container_id")
