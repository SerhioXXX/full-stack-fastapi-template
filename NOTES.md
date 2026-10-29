# Notes for reviewers

## What was delivered

- RBAC with three roles (`admin`, `manager`, `member`) and a documented permission matrix.
- Backend enforcement via a central policy map + `require_permission(...)` FastAPI dependencies.
- Frontend UX: hide nav by permission, Access Denied page on deep links, role selector in admin UI.
- Stub surfaces: `GET /metrics/`, `GET/PATCH /settings/system` (in-memory settings).
- Focused backend tests for critical allow/deny paths.
- Docker Compose–first local workflow with seeded demo users.

## Trade-offs

1. **Permission strings over role-only checks**  
   Routes declare *what* they need (`users:list`), not *who* may call them. Extending access is usually a one-line matrix change. Slightly more code than `if role in (...)`.

2. **`permissions[]` on `/users/me` (and `UserPublic`)**  
   Frontend does not duplicate the matrix. Slightly larger JSON payloads; UI must still treat the API as authoritative.

3. **System settings are in-memory**  
   Enough to demonstrate `settings:write` and admin-only UI. Restarts reset values. Persisting to Postgres would be the next step.

4. **`is_superuser` retained**  
   Kept in sync with `role == admin` so existing item ownership checks and gradual migration stay simple. Long-term: drop the column once all call sites use roles/permissions.

5. **Items module**  
   Still uses legacy `is_superuser` for “see all items”. Out of the assignment’s RBAC surface; not redesigned into the permission matrix.

6. **Shared DB for pytest and local app**  
   Template tests hit the same Postgres. Teardown now re-seeds demo users. Ideal follow-up: a dedicated test database URL.

## What we would do with more time

- Persist system settings; add audit log for setting changes and authz denials.
- Drop `is_superuser`; migrate item admin checks to permissions (e.g. `items:read_all`).
- Playwright smoke tests per role (nav visibility + forbidden deep link).
- Isolate pytest DB from the demo stack.
- Fine-grained “assign role X” rules (e.g. managers cannot create admins — today only admins create users at all).

## Scope intentionally not cut

- Server-side authorization on the protected surface.
- Permission matrix documented and applied on backend + frontend.
- Critical allow/deny backend tests.
- Runnable Docker setup with seed users.
