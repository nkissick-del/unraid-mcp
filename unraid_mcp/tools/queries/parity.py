"""GraphQL mutations and queries for parity check management."""

PARITY_CHECK_RETURN_FIELDS = """
    id
    state
    progress
    speed
    errors
    startedAt
"""

PARITY_CHECK_MUTATIONS: dict[str, str] = {
    "START": f"""
        mutation StartParityCheck($correct: Boolean!) {{
          parityCheck {{
            start(correct: $correct) {{
              {PARITY_CHECK_RETURN_FIELDS}
            }}
          }}
        }}
    """,
    "PAUSE": f"""
        mutation PauseParityCheck {{
          parityCheck {{
            pause {{
              {PARITY_CHECK_RETURN_FIELDS}
            }}
          }}
        }}
    """,
    "RESUME": f"""
        mutation ResumeParityCheck {{
          parityCheck {{
            resume {{
              {PARITY_CHECK_RETURN_FIELDS}
            }}
          }}
        }}
    """,
    "CANCEL": f"""
        mutation CancelParityCheck {{
          parityCheck {{
            cancel {{
              {PARITY_CHECK_RETURN_FIELDS}
            }}
          }}
        }}
    """,
}

PARITY_STATUS_QUERY = """
    query GetParityStatus {
      array {
        id
        state
      }
    }
"""
