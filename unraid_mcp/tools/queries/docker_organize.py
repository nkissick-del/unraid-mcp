"""GraphQL mutations for Docker organization and template management."""

CREATE_DOCKER_FOLDER_MUTATION = """
    mutation CreateDockerFolder($name: String!, $icon: String) {
      docker {
        createFolder(name: $name, icon: $icon) {
          id
          name
          icon
        }
      }
    }
"""

SET_DOCKER_FOLDER_CHILDREN_MUTATION = """
    mutation SetDockerFolderChildren($folderId: String!, $children: [String!]!) {
      docker {
        setFolderChildren(folderId: $folderId, children: $children) {
          id
          name
        }
      }
    }
"""

DELETE_DOCKER_ENTRIES_MUTATION = """
    mutation DeleteDockerEntries($ids: [String!]!) {
      docker {
        deleteEntries(ids: $ids) {
          success
        }
      }
    }
"""

MOVE_DOCKER_ENTRIES_TO_FOLDER_MUTATION = """
    mutation MoveDockerEntriesToFolder($folderId: String!, $entryIds: [String!]!) {
      docker {
        moveEntriesToFolder(folderId: $folderId, entryIds: $entryIds) {
          success
        }
      }
    }
"""

MOVE_DOCKER_ITEMS_TO_POSITION_MUTATION = """
    mutation MoveDockerItemsToPosition($itemIds: [String!]!, $position: Int!) {
      docker {
        moveItemsToPosition(itemIds: $itemIds, position: $position) {
          success
        }
      }
    }
"""

RENAME_DOCKER_FOLDER_MUTATION = """
    mutation RenameDockerFolder($folderId: String!, $name: String!) {
      docker {
        renameFolder(folderId: $folderId, name: $name) {
          id
          name
        }
      }
    }
"""

CREATE_DOCKER_FOLDER_WITH_ITEMS_MUTATION = """
    mutation CreateDockerFolderWithItems($name: String!, $itemIds: [String!]!) {
      docker {
        createFolderWithItems(name: $name, itemIds: $itemIds) {
          id
          name
        }
      }
    }
"""

UPDATE_DOCKER_VIEW_PREFERENCES_MUTATION = """
    mutation UpdateDockerViewPreferences($input: DockerViewPreferencesInput!) {
      docker {
        updateViewPreferences(input: $input) {
          success
        }
      }
    }
"""

SYNC_DOCKER_TEMPLATE_PATHS_MUTATION = """
    mutation SyncDockerTemplatePaths {
      docker {
        syncTemplatePaths {
          success
        }
      }
    }
"""

RESET_DOCKER_TEMPLATE_MAPPINGS_MUTATION = """
    mutation ResetDockerTemplateMappings {
      docker {
        resetTemplateMappings {
          success
        }
      }
    }
"""

REFRESH_DOCKER_DIGESTS_MUTATION = """
    mutation RefreshDockerDigests {
      docker {
        refreshDigests {
          success
        }
      }
    }
"""
