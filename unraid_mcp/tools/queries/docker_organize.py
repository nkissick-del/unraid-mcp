"""GraphQL mutations for Docker organization and template management."""

CREATE_DOCKER_FOLDER_MUTATION = """
    mutation CreateDockerFolder($name: String!, $icon: String) {
      createDockerFolder(name: $name, icon: $icon) {
        id
        name
        icon
      }
    }
"""

SET_DOCKER_FOLDER_CHILDREN_MUTATION = """
    mutation SetDockerFolderChildren($folderId: String, $children: [String!]!) {
      setDockerFolderChildren(folderId: $folderId, childrenIds: $children) {
        id
        name
      }
    }
"""

DELETE_DOCKER_ENTRIES_MUTATION = """
    mutation DeleteDockerEntries($ids: [String!]!) {
      deleteDockerEntries(entryIds: $ids) {
        success
      }
    }
"""

MOVE_DOCKER_ENTRIES_TO_FOLDER_MUTATION = """
    mutation MoveDockerEntriesToFolder($folderId: String!, $entryIds: [String!]!) {
      moveDockerEntriesToFolder(sourceEntryIds: $entryIds, destinationFolderId: $folderId) {
        success
      }
    }
"""

MOVE_DOCKER_ITEMS_TO_POSITION_MUTATION = """
    mutation MoveDockerItemsToPosition($itemIds: [String!]!, $position: Float!) {
      moveDockerItemsToPosition(sourceEntryIds: $itemIds, destinationFolderId: "", position: $position) {
        success
      }
    }
"""

RENAME_DOCKER_FOLDER_MUTATION = """
    mutation RenameDockerFolder($folderId: String!, $name: String!) {
      renameDockerFolder(folderId: $folderId, newName: $name) {
        id
        name
      }
    }
"""

CREATE_DOCKER_FOLDER_WITH_ITEMS_MUTATION = """
    mutation CreateDockerFolderWithItems($name: String!, $itemIds: [String!]!) {
      createDockerFolderWithItems(name: $name, sourceEntryIds: $itemIds) {
        id
        name
      }
    }
"""

UPDATE_DOCKER_VIEW_PREFERENCES_MUTATION = """
    mutation UpdateDockerViewPreferences($viewId: String, $prefs: JSON!) {
      updateDockerViewPreferences(viewId: $viewId, prefs: $prefs) {
        success
      }
    }
"""

SYNC_DOCKER_TEMPLATE_PATHS_MUTATION = """
    mutation SyncDockerTemplatePaths {
      syncDockerTemplatePaths {
        scanned
        matched
        skipped
        errors
      }
    }
"""

RESET_DOCKER_TEMPLATE_MAPPINGS_MUTATION = """
    mutation ResetDockerTemplateMappings {
      resetDockerTemplateMappings
    }
"""

REFRESH_DOCKER_DIGESTS_MUTATION = """
    mutation RefreshDockerDigests {
      refreshDockerDigests
    }
"""
