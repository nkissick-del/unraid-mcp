"""GraphQL queries and mutations for Docker container management."""

# Pre-built mutation queries keyed by action — eliminates f-string interpolation of user input
DOCKER_ACTION_MUTATIONS: dict[str, str] = {
    "start": """
        mutation ManageDockerContainer($id: PrefixedID!) {
          docker {
            start(id: $id) {
              id
              names
              state
              status
            }
          }
        }
    """,
    "stop": """
        mutation ManageDockerContainer($id: PrefixedID!) {
          docker {
            stop(id: $id) {
              id
              names
              state
              status
            }
          }
        }
    """,
    "pause": """
        mutation ManageDockerContainer($id: PrefixedID!) {
          docker {
            pause(id: $id) {
              id
              names
              state
              status
            }
          }
        }
    """,
    "unpause": """
        mutation ManageDockerContainer($id: PrefixedID!) {
          docker {
            unpause(id: $id) {
              id
              names
              state
              status
            }
          }
        }
    """,
}

CONTAINER_LIST_FIELDS = """
    id
    names
    image
    state
    status
    autoStart
"""

DOCKER_REMOVE_CONTAINER_MUTATION = """
    mutation RemoveDockerContainer($id: PrefixedID!, $withImage: Boolean) {
      docker {
        removeContainer(id: $id, withImage: $withImage)
      }
    }
"""

DOCKER_UPDATE_CONTAINER_MUTATION = """
    mutation UpdateDockerContainer($id: PrefixedID!) {
      docker {
        updateContainer(id: $id) {
          id
          names
          state
          status
          image
        }
      }
    }
"""

DOCKER_LOGS_QUERY = """
    query DockerContainerLogs($id: PrefixedID!, $since: DateTime, $tail: Int) {
      docker {
        logs(id: $id, since: $since, tail: $tail) {
          containerId
          lines {
            timestamp
            message
          }
          cursor
        }
      }
    }
"""
