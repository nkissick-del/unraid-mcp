"""GraphQL queries and mutations for array management."""

ARRAY_SET_STATE_MUTATION = """
    mutation SetArrayState($input: ArrayStateInput!) {
      array {
        setState(input: $input) {
          id
          state
          capacity {
            disks {
              free
              size
            }
          }
        }
      }
    }
"""

ARRAY_STATUS_QUERY = """
    query GetArrayStatus {
      array {
        status {
          id
          state
          capacity {
            disks {
              free
              size
            }
          }
        }
      }
    }
"""
