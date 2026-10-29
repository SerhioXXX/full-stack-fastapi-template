# ADR 0002: Expose `permissions[]` on `UserPublic`

**Status:** Accepted  
**Date:** 2026-10-30  
**Related:** [DECISION.md — D3](../../DECISION.md)

## Context

The UI must hide inaccessible navigation and show Access Denied on deep links without re-implementing the server matrix.

## Decision

Populate `permissions: string[]` on `UserPublic` (including `GET /users/me`) from the same `ROLE_PERMISSIONS` map used by `require_permission`.

Frontend uses `can(user, permission)` only for UX; the API remains the security boundary.

## Consequences

- One source of truth for capabilities (backend policy module).
- Client types come from OpenAPI regeneration after schema changes.
- Slightly larger user payloads; acceptable for this app size.
