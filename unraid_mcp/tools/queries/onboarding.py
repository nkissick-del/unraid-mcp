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
          status
          completed
          completedAtVersion
        }
      }
    }
"""

RESET_ONBOARDING_MUTATION = """
    mutation ResetOnboarding {
      onboarding {
        resetOnboarding {
          status
          completed
          completedAtVersion
        }
      }
    }
"""

OPEN_ONBOARDING_MUTATION = """
    mutation OpenOnboarding {
      onboarding {
        openOnboarding {
          status
          completed
          completedAtVersion
        }
      }
    }
"""

CLOSE_ONBOARDING_MUTATION = """
    mutation CloseOnboarding {
      onboarding {
        closeOnboarding {
          status
          completed
          completedAtVersion
        }
      }
    }
"""

BYPASS_ONBOARDING_MUTATION = """
    mutation BypassOnboarding {
      onboarding {
        bypassOnboarding {
          status
          completed
          completedAtVersion
        }
      }
    }
"""

RESUME_ONBOARDING_MUTATION = """
    mutation ResumeOnboarding {
      onboarding {
        resumeOnboarding {
          status
          completed
          completedAtVersion
        }
      }
    }
"""

SET_ONBOARDING_OVERRIDE_MUTATION = """
    mutation SetOnboardingOverride($input: OnboardingOverrideInput!) {
      onboarding {
        setOnboardingOverride(input: $input) {
          status
          completed
          completedAtVersion
        }
      }
    }
"""

CLEAR_ONBOARDING_OVERRIDE_MUTATION = """
    mutation ClearOnboardingOverride {
      onboarding {
        clearOnboardingOverride {
          status
          completed
          completedAtVersion
        }
      }
    }
"""

CREATE_INTERNAL_BOOT_POOL_MUTATION = """
    mutation CreateInternalBootPool($input: CreateInternalBootPoolInput!) {
      onboarding {
        createInternalBootPool(input: $input) {
          ok
          code
          output
        }
      }
    }
"""

REFRESH_INTERNAL_BOOT_CONTEXT_MUTATION = """
    mutation RefreshInternalBootContext {
      onboarding {
        refreshInternalBootContext {
          arrayStopped
          bootEligible
          bootedFromFlashWithInternalBootSetup
          enableBootTransfer
        }
      }
    }
"""
