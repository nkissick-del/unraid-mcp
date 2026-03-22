"""GraphQL queries and mutations for onboarding management."""

IS_FRESH_INSTALL_QUERY = """
    query IsFreshInstall {
      isFreshInstall
    }
"""

COMPLETE_ONBOARDING_MUTATION = """
    mutation CompleteOnboarding {
      onboarding {
        completeOnboarding {
          success
        }
      }
    }
"""

RESET_ONBOARDING_MUTATION = """
    mutation ResetOnboarding {
      onboarding {
        resetOnboarding {
          success
        }
      }
    }
"""

OPEN_ONBOARDING_MUTATION = """
    mutation OpenOnboarding {
      onboarding {
        openOnboarding {
          success
        }
      }
    }
"""

CLOSE_ONBOARDING_MUTATION = """
    mutation CloseOnboarding {
      onboarding {
        closeOnboarding {
          success
        }
      }
    }
"""

BYPASS_ONBOARDING_MUTATION = """
    mutation BypassOnboarding {
      onboarding {
        bypassOnboarding {
          success
        }
      }
    }
"""

RESUME_ONBOARDING_MUTATION = """
    mutation ResumeOnboarding {
      onboarding {
        resumeOnboarding {
          success
        }
      }
    }
"""

SET_ONBOARDING_OVERRIDE_MUTATION = """
    mutation SetOnboardingOverride($input: OnboardingOverrideInput!) {
      onboarding {
        setOnboardingOverride(input: $input) {
          success
        }
      }
    }
"""

CLEAR_ONBOARDING_OVERRIDE_MUTATION = """
    mutation ClearOnboardingOverride {
      onboarding {
        clearOnboardingOverride {
          success
        }
      }
    }
"""

CREATE_INTERNAL_BOOT_POOL_MUTATION = """
    mutation CreateInternalBootPool($input: CreateInternalBootPoolInput!) {
      onboarding {
        createInternalBootPool(input: $input) {
          success
        }
      }
    }
"""

REFRESH_INTERNAL_BOOT_CONTEXT_MUTATION = """
    mutation RefreshInternalBootContext {
      onboarding {
        refreshInternalBootContext {
          success
        }
      }
    }
"""
