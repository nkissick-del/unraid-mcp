"""GraphQL queries for system-extra and metrics tools."""

SYSTEM_METRICS_QUERY = """
    query GetSystemMetrics {
      metrics {
        id
        cpu {
          id
          percentTotal
          cpus {
            percentTotal
            percentUser
            percentSystem
            percentIdle
          }
        }
        memory {
          id
          total
          used
          free
          available
          active
          buffcache
          percentTotal
          swapTotal
          swapUsed
          swapFree
          percentSwapTotal
        }
        temperature {
          id
          sensors {
            id
            name
            type
            location
            current { value unit timestamp status }
            warning
            critical
          }
          summary {
            average
            warningCount
            criticalCount
          }
        }
      }
    }
"""

PARITY_HISTORY_QUERY = """
    query GetParityHistory {
      parityHistory {
        date
        speed
        status
        correcting
        progress
        paused
        running
      }
    }
"""
