# Decision Log

## Decision 1
- **Date:** [Date]
- **Context:** [Context]
- **Decision:** [Decision]
- **Alternatives Considered:** [Alternatives]
- **Consequences:** [Consequences]

## Decision 2
- **Date:** [Date]
- **Context:** [Context]
- **Decision:** [Decision]
- **Alternatives Considered:** [Alternatives]
- **Consequences:** [Consequences]

## Contentful Management SDK Bug - defaultValue None Issue
- **Date:** 2025-09-06 4:27:58 PM
- **Author:** Unknown User
- **Context:** While implementing live Contentful integration, encountered a critical bug in the contentful-management Python SDK (v2.13.1) that prevented adding new fields to content types.
- **Decision:** Use direct HTTP API calls instead of SDK for content model modifications
- **Alternatives Considered:**
  - Use SDK as intended
  - Manual field creation through web interface
  - Find alternative Python SDK
  - Submit bug report and wait for fix
- **Consequences:**
  - Successful field addition without SDK limitations
  - More control over API payloads
  - Need to handle versioning and headers manually
  - Bypassed SDK abstraction layer
  - Future content model changes should use same approach
