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
}

CONTAINER_LIST_FIELDS = """
    id
    names
    image
    state
    status
    autoStart
"""
