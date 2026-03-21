"""GraphQL queries and mutations for onboarding management."""

IS_FRESH_INSTALL_QUERY = """
    query IsFreshInstall {
      freshInstall
    }
"""

COMPLETE_ONBOARDING_MUTATION = """
    mutation CompleteOnboarding {
      onboarding {
        complete {
          success
        }
      }
    }
"""

RESET_ONBOARDING_MUTATION = """
    mutation ResetOnboarding {
      onboarding {
        reset {
          success
        }
      }
    }
"""

OPEN_ONBOARDING_MUTATION = """
    mutation OpenOnboarding {
      onboarding {
        open {
          success
        }
      }
    }
"""

CLOSE_ONBOARDING_MUTATION = """
    mutation CloseOnboarding {
      onboarding {
        close {
          success
        }
      }
    }
"""

BYPASS_ONBOARDING_MUTATION = """
    mutation BypassOnboarding {
      onboarding {
        bypass {
          success
        }
      }
    }
"""

RESUME_ONBOARDING_MUTATION = """
    mutation ResumeOnboarding {
      onboarding {
        resume {
          success
        }
      }
    }
"""

SET_ONBOARDING_OVERRIDE_MUTATION = """
    mutation SetOnboardingOverride($input: OnboardingOverrideInput!) {
      onboarding {
        setOverride(input: $input) {
          success
        }
      }
    }
"""

CLEAR_ONBOARDING_OVERRIDE_MUTATION = """
    mutation ClearOnboardingOverride {
      onboarding {
        clearOverride {
          success
        }
      }
    }
"""

CREATE_INTERNAL_BOOT_POOL_MUTATION = """
    mutation CreateInternalBootPool {
      onboarding {
        createInternalBootPool {
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
