"""GraphQL queries and mutations for API key and auth management."""

LIST_API_KEYS_QUERY = """
    query ListApiKeys {
      apiKeys {
        id
        name
        roles
        description
        createdAt
        lastUsedAt
      }
    }
"""

GET_API_KEY_QUERY = """
    query GetApiKey($keyId: PrefixedID!) {
      apiKey(id: $keyId) {
        id
        name
        roles
        description
        permissions
        createdAt
        lastUsedAt
      }
    }
"""

GET_API_KEY_POSSIBLE_ROLES_QUERY = """
    query GetApiKeyPossibleRoles {
      apiKeyPossibleRoles {
        id
        name
        description
      }
    }
"""

GET_API_KEY_POSSIBLE_PERMISSIONS_QUERY = """
    query GetApiKeyPossiblePermissions {
      apiKeyPossiblePermissions {
        id
        name
        description
        category
      }
    }
"""

GET_PERMISSIONS_FOR_ROLES_QUERY = """
    query GetPermissionsForRoles($roles: [String!]!) {
      getPermissionsForRoles(roles: $roles) {
        resource
        actions
      }
    }
"""

PREVIEW_EFFECTIVE_PERMISSIONS_QUERY = """
    query PreviewEffectivePermissions($roles: [String!]!, $permissions: [String!]!) {
      previewEffectivePermissions(roles: $roles, permissions: $permissions) {
        resource
        actions
      }
    }
"""

GET_AVAILABLE_AUTH_ACTIONS_QUERY = """
    query GetAvailableAuthActions {
      getAvailableAuthActions {
        id
        name
        description
      }
    }
"""

GET_API_KEY_CREATION_FORM_SCHEMA_QUERY = """
    query GetApiKeyCreationFormSchema {
      getApiKeyCreationFormSchema {
        fields
        validation
      }
    }
"""

CREATE_API_KEY_MUTATION = """
    mutation CreateApiKey($input: CreateApiKeyInput!) {
      apiKey {
        create(input: $input) {
          id
          name
          key
          roles
        }
      }
    }
"""

ADD_ROLE_TO_API_KEY_MUTATION = """
    mutation AddRoleToApiKey($input: AddRoleForApiKeyInput!) {
      apiKey {
        addRole(input: $input) {
          id
          name
          roles
        }
      }
    }
"""

REMOVE_ROLE_FROM_API_KEY_MUTATION = """
    mutation RemoveRoleFromApiKey($input: RemoveRoleFromApiKeyInput!) {
      apiKey {
        removeRole(input: $input) {
          id
          name
          roles
        }
      }
    }
"""

DELETE_API_KEY_MUTATION = """
    mutation DeleteApiKey($input: DeleteApiKeyInput!) {
      apiKey {
        delete(input: $input) {
          success
        }
      }
    }
"""

UPDATE_API_KEY_MUTATION = """
    mutation UpdateApiKey($input: UpdateApiKeyInput!) {
      apiKey {
        update(input: $input) {
          id
          name
          roles
          description
        }
      }
    }
"""
