"""GraphQL mutations for Docker batch operations."""

DOCKER_UPDATE_CONTAINERS_MUTATION = """
    mutation UpdateDockerContainers($ids: [PrefixedID!]!) {
      docker {
        updateContainers(ids: $ids) {
          id
          names
          state
          status
          image
        }
      }
    }
"""

DOCKER_UPDATE_ALL_CONTAINERS_MUTATION = """
    mutation UpdateAllDockerContainers {
      docker {
        updateAllContainers {
          id
          names
          state
          status
          image
        }
      }
    }
"""

DOCKER_UPDATE_AUTOSTART_MUTATION = """
    mutation UpdateDockerAutostart($input: AutostartConfigurationInput!) {
      docker {
        updateAutostartConfiguration(input: $input) {
          id
          names
          autoStart
        }
      }
    }
"""
