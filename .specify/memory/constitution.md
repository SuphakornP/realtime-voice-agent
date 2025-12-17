<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║                           SYNC IMPACT REPORT                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Version Change: 0.0.0 → 1.0.0 (MAJOR - Initial constitution ratification)    ║
║                                                                              ║
║ Added Principles:                                                            ║
║   • I. RESTful API Design Standards                                          ║
║   • II. Comprehensive Error Handling                                         ║
║   • III. Input Validation                                                    ║
║   • IV. Security Best Practices                                              ║
║   • V. Test Coverage Requirements                                            ║
║                                                                              ║
║ Added Sections:                                                              ║
║   • Technology Standards                                                     ║
║   • Quality Gates                                                            ║
║   • Governance                                                               ║
║                                                                              ║
║ Templates Status:                                                            ║
║   • .specify/templates/plan-template.md ✅ Compatible                        ║
║   • .specify/templates/spec-template.md ✅ Compatible                        ║
║   • .specify/templates/tasks-template.md ✅ Compatible                       ║
║                                                                              ║
║ Follow-up TODOs: None                                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
-->

# Realtime Voice Agent POC Constitution

## Core Principles

### I. RESTful API Design Standards

All API endpoints MUST adhere to RESTful design principles:

- **Resource-Oriented URLs**: Use nouns for resources (`/agents`, `/sessions`), not verbs
- **HTTP Methods**: Use appropriate methods - GET (read), POST (create), PUT (full update), PATCH (partial update), DELETE (remove)
- **Status Codes**: Return semantically correct HTTP status codes:
  - `200 OK` for successful GET/PUT/PATCH
  - `201 Created` for successful POST
  - `204 No Content` for successful DELETE
  - `400 Bad Request` for validation errors
  - `401 Unauthorized` for authentication failures
  - `403 Forbidden` for authorization failures
  - `404 Not Found` for missing resources
  - `422 Unprocessable Entity` for business logic errors
  - `500 Internal Server Error` for unexpected failures
- **Versioning**: APIs MUST be versioned via URL path (`/api/v1/`) or header
- **Pagination**: Collection endpoints MUST support pagination with `limit`, `offset`, and return `total_count`
- **Consistent Response Format**: All responses MUST follow a consistent JSON structure

**Rationale**: Consistent API design reduces integration friction, improves developer experience, and enables predictable client behavior.

### II. Comprehensive Error Handling

All errors MUST be handled explicitly and provide actionable information:

- **Structured Error Responses**: All errors MUST return JSON with:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human-readable message",
      "details": {},
      "request_id": "uuid"
    }
  }
  ```
- **Error Codes**: Define domain-specific error codes (e.g., `VOICE_SESSION_EXPIRED`, `AUDIO_FORMAT_UNSUPPORTED`)
- **No Silent Failures**: Exceptions MUST NOT be swallowed; log and propagate appropriately
- **Graceful Degradation**: Services MUST handle downstream failures gracefully with fallbacks where possible
- **Logging**: All errors MUST be logged with correlation IDs for traceability
- **User-Facing Messages**: Error messages shown to users MUST be clear and actionable, never expose stack traces

**Rationale**: Proper error handling improves debuggability, user experience, and system reliability.

### III. Input Validation

All external inputs MUST be validated before processing:

- **Validate at Boundary**: Validate all inputs at API entry points before business logic
- **Schema Validation**: Use schema validation (Pydantic, JSON Schema) for request bodies
- **Type Coercion**: Explicitly define and validate types; reject invalid types
- **Constraints**: Enforce constraints (min/max length, patterns, ranges, enums)
- **Sanitization**: Sanitize inputs to prevent injection attacks (SQL, XSS, command injection)
- **Fail Fast**: Return `400 Bad Request` with specific field-level errors immediately on validation failure
- **Validation Error Format**:
  ```json
  {
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Input validation failed",
      "details": {
        "fields": [
          {"field": "audio_format", "message": "Must be one of: pcm16, g711_ulaw, g711_alaw"}
        ]
      }
    }
  }
  ```

**Rationale**: Input validation prevents security vulnerabilities, data corruption, and provides clear feedback to API consumers.

### IV. Security Best Practices

Security MUST be built into every layer of the application:

- **Authentication**: All endpoints (except health checks) MUST require authentication
- **Authorization**: Implement role-based or attribute-based access control; verify permissions on every request
- **API Keys**: Store API keys and secrets in environment variables or secret managers; NEVER commit to version control
- **HTTPS Only**: All communications MUST use TLS/HTTPS in production
- **Rate Limiting**: Implement rate limiting to prevent abuse (e.g., 100 requests/minute per API key)
- **CORS**: Configure CORS policies explicitly; avoid wildcard (`*`) in production
- **Headers**: Set security headers (Content-Security-Policy, X-Content-Type-Options, X-Frame-Options)
- **Dependency Security**: Regularly audit and update dependencies for known vulnerabilities
- **Audit Logging**: Log all authentication attempts, authorization failures, and sensitive operations
- **Data Protection**: Encrypt sensitive data at rest and in transit; mask PII in logs

**Rationale**: Security is non-negotiable; breaches damage trust and can have legal/financial consequences.

### V. Test Coverage Requirements

All code MUST meet minimum test coverage standards:

- **Minimum Coverage**: 80% line coverage for all modules; 90% for critical paths (auth, payments, voice processing)
- **Test Types Required**:
  - **Unit Tests**: Test individual functions/methods in isolation
  - **Integration Tests**: Test component interactions and external service integrations
  - **Contract Tests**: Validate API contracts match specifications
  - **End-to-End Tests**: Test critical user journeys
- **Test-First Encouraged**: Write tests before implementation when possible (TDD)
- **No Untested Code in Production**: All merged code MUST have corresponding tests
- **Test Quality**:
  - Tests MUST be deterministic (no flaky tests)
  - Tests MUST be independent (no shared state between tests)
  - Tests MUST be fast (unit tests < 100ms each)
- **CI/CD Gate**: Tests MUST pass before merge; coverage drops MUST block PR

**Rationale**: High test coverage catches regressions early, enables confident refactoring, and documents expected behavior.

## Technology Standards

### Stack Requirements

- **Language**: Python 3.9+
- **Framework**: OpenAI Agents SDK with voice support
- **Audio Formats**: PCM16 (primary), G.711 μ-law/A-law (telephony)
- **API Style**: RESTful for HTTP endpoints, WebSocket for realtime audio
- **Testing**: pytest with pytest-asyncio for async tests
- **Linting**: ruff or flake8 with strict configuration
- **Type Checking**: mypy with strict mode enabled

### Documentation Requirements

- All public APIs MUST have OpenAPI/Swagger documentation
- All functions MUST have docstrings with parameter and return type descriptions
- README MUST include setup instructions, environment variables, and quickstart guide

## Quality Gates

### Pre-Commit Checks

1. Linting passes with zero errors
2. Type checking passes with zero errors
3. All tests pass
4. Coverage threshold met (80% minimum)

### Pre-Merge Checks

1. All pre-commit checks pass
2. Code review approved by at least one reviewer
3. No unresolved security vulnerabilities in dependencies
4. API documentation updated if endpoints changed

### Pre-Deploy Checks

1. All pre-merge checks pass
2. Integration tests pass against staging environment
3. Performance benchmarks within acceptable thresholds
4. Rollback plan documented

## Governance

- This constitution supersedes all other development practices for this project
- Amendments require:
  1. Written proposal with rationale
  2. Review of impact on existing code
  3. Migration plan if breaking changes
  4. Version increment following semantic versioning
- All code reviews MUST verify compliance with these principles
- Violations MUST be documented and justified in PR description
- Use `documents/PRD_Voice_Agent_POC.md` for feature requirements and technical context

**Version**: 1.0.0 | **Ratified**: 2025-12-15 | **Last Amended**: 2025-12-15
