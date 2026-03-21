"""GraphQL queries and mutations for customization settings."""

DISPLAY_SETTINGS_QUERY = """
    query GetDisplaySettings {
      display {
        id
        locale
        theme
        dateFormat
        timeFormat
        numberFormat
        startPage
      }
    }
"""

CURRENT_USER_QUERY = """
    query GetCurrentUser {
      me {
        id
        name
        description
        role
        permissions
      }
    }
"""

OWNER_INFO_QUERY = """
    query GetOwnerInfo {
      owner {
        id
        username
        url
        avatar
      }
    }
"""

CUSTOMIZATION_QUERY = """
    query GetCustomization {
      customization {
        id
        theme
        locale
        dateFormat
        timeFormat
        banner
        usage
      }
    }
"""

PUBLIC_THEME_QUERY = """
    query GetPublicTheme {
      publicTheme {
        id
        theme
        banner
      }
    }
"""

SET_THEME_MUTATION = """
    mutation SetTheme($input: ThemeInput!) {
      setTheme(input: $input) {
        theme
        banner
      }
    }
"""

SET_LOCALE_MUTATION = """
    mutation SetLocale($locale: String!) {
      setLocale(locale: $locale) {
        locale
      }
    }
"""
