"""GraphQL queries and mutations for customization settings."""

DISPLAY_SETTINGS_QUERY = """
    query GetDisplaySettings {
      display {
        id
        case { id url icon error }
        theme
        unit
        scale
        tabs
        resize
        wwn
        total
        usage
        text
        warning
        critical
        hot
        max
        locale
      }
    }
"""

CURRENT_USER_QUERY = """
    query GetCurrentUser {
      me {
        id
        name
        description
        roles
        permissions
      }
    }
"""

OWNER_INFO_QUERY = """
    query GetOwnerInfo {
      owner {
        username
        url
        avatar
      }
    }
"""

CUSTOMIZATION_QUERY = """
    query GetCustomization {
      customization {
        activationCode { code }
        onboarding { status completed completedAtVersion }
      }
    }
"""

PUBLIC_THEME_QUERY = """
    query GetPublicTheme {
      publicTheme {
        name
        showBannerImage
        showBannerGradient
        showHeaderDescription
        headerBackgroundColor
        headerPrimaryTextColor
        headerSecondaryTextColor
      }
    }
"""

SET_THEME_MUTATION = """
    mutation SetTheme($theme: ThemeName!) {
      customization {
        setTheme(theme: $theme) {
          theme
          banner
        }
      }
    }
"""

SET_LOCALE_MUTATION = """
    mutation SetLocale($locale: String!) {
      customization {
        setLocale(locale: $locale) {
          locale
        }
      }
    }
"""
