# ADR 0001: Permission-based FastAPI dependencies

**Status:** Accepted  
**Date:** 2026-10-30  
**Related:** [DECISION.md — D2](../../DECISION.md)

## Context

The template gated admin APIs with `is_superuser`. We need three roles and a clear, extensible authorization model.

## Decision

Use a central `ROLE_PERMISSIONS` map and `Depends(require_permission("…"))` on routes.

- Policy: `backend/app/core/rbac.py`
- Dependency factory: `require_permission` in `backend/app/api/deps.py`
- Denied calls: HTTP 403 + WARNING log

## Consequences

- Adding or changing access is usually a matrix edit, not a hunt across handlers.
- Call sites read as capability checks (`users:list`) rather than role lists.
- Object-level rules (own profile, own items) remain explicit beside the matrix.
