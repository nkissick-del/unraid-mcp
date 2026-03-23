"""GraphQL queries and mutations for Unraid Connect administration."""

GET_CONNECT_INFO_QUERY = """
    query GetConnectInfo {
      connect {
        id
        dynamicRemoteAccess { enabledType runningType error }
        settings { id dataSchema uiSchema }
      }
    }
"""

GET_REMOTE_ACCESS_QUERY = """
    query GetRemoteAccess {
      remoteAccess {
        accessType
        forwardType
        port
      }
    }
"""

GET_CLOUD_INFO_QUERY = """
    query GetCloudInfo {
      cloud {
        error
        apiKey { valid error }
        relay { status timeout error }
        minigraphql { status timeout error }
        cloud { status ip error }
        allowedOrigins
      }
    }
"""

UPDATE_API_SETTINGS_MUTATION = """
    mutation UpdateApiSettings($input: ConnectSettingsInput!) {
      updateApiSettings(input: $input) {
        success
      }
    }
"""

CONNECT_SIGN_IN_MUTATION = """
    mutation ConnectSignIn($input: ConnectSignInInput!) {
      connectSignIn(input: $input) {
        success
      }
    }
"""

CONNECT_SIGN_OUT_MUTATION = """
    mutation ConnectSignOut {
      connectSignOut {
        success
      }
    }
"""

SETUP_REMOTE_ACCESS_MUTATION = """
    mutation SetupRemoteAccess($input: RemoteAccessInput!) {
      setupRemoteAccess(input: $input) {
        enabled
        url
        type
        port
        status
      }
    }
"""

ENABLE_DYNAMIC_REMOTE_ACCESS_MUTATION = """
    mutation EnableDynamicRemoteAccess($input: DynamicRemoteAccessInput!) {
      enableDynamicRemoteAccess(input: $input) {
        enabled
        url
        type
        port
        status
      }
    }
"""
