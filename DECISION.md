# Architecture Decisions — RBAC

This document records the design choices for adding Role-Based Access Control to the Full Stack FastAPI Template (`TASK.md`).

The executable work plan lives in [`PLAN.md`](./PLAN.md).

---

## Context

The template today uses a binary flag `User.is_superuser`:

- Backend: `get_current_active_superuser` gates user management and a few admin utilities.
- Frontend: sidebar and `/admin` route check `user.is_superuser`.

The assignment requires three roles (`admin`, `manager`, `member`), a documented permission matrix enforced on **both** backend and frontend, focused tests, and clear documentation. We are **not** hard time-boxed, so we prefer a maintainable permission layer over the smallest possible patch.

---

## Decision index

| ID | Topic | Choice |
|----|--------|--------|
| D1 | Role storage | **1A** — `role` enum/column as source of truth |
| D2 | Backend authorization pattern | **2A** — permission-based FastAPI dependencies |
| D3 | How the frontend learns capabilities | **3B** — `/users/me` (and public user shape) returns `permissions[]` |
| D4 | “Global settings” surface | **4A** — admin-only System Settings stub |
| D5 | Local development workflow | **5A** — Docker Compose |

---

## D1 — Role storage (1A)

### Problem

We need three named roles with different capabilities. The existing `is_superuser: bool` cannot express `manager` vs `member`.

### Options considered

| Option | Description |
|--------|-------------|
| **A (chosen)** | Add `User.role` (`admin` \| `manager` \| `member`) as the authority |
| B | Keep `is_superuser` and add `role` as a second field without a single source of truth |
| C | Separate `Role` table and user–role M2M (or full RBAC tables) |

### Decision

Implement **Option A**.

- Add a `Role` enum and a non-null `role` column (default `member`).
- Migrate existing rows: `is_superuser=True` → `admin`, otherwise → `member`.
- Treat `is_superuser` as a **derived compatibility field** during transition:
  - Writers that set `role` also sync `is_superuser` (`True` iff `admin`).
  - New authorization code must check permissions / `role`, not `is_superuser`.
- Admin UI replaces the “Is superuser?” checkbox with a role selector.

### Rationale

- Matches the assignment’s role vocabulary directly.
- One place to reason about access (`role` → permissions).
- Option B creates conflicting signals (`is_superuser=True` but `role=member`).
- Option C is correct for large multi-tenant products but adds tables, joins, and UI without benefit for three fixed roles.

### Consequences

- Alembic migration and schema/API updates are required.
- Seed data and tests must create users with explicit roles.
- Any remaining `is_superuser` checks on the RBAC surface should be removed or redirected to permissions to avoid dual logic.

---

## D2 — Backend authorization pattern (2A)

### Problem

Authorization must be consistent, easy to extend (new role or permission without editing many handlers), and obvious to a teammate within minutes.

### Options considered

| Option | Description |
|--------|-------------|
| **A (chosen)** | Central permission map + `Depends(require_permission("…"))` |
| B | Role-only dependencies, e.g. `require_roles(ADMIN, MANAGER)` |
| C | Inline `if current_user.role == …` inside each endpoint |

### Decision

Implement **Option A**.

Structure (illustrative):

1. **Permission keys** as stable strings, e.g. `users:list`, `users:create`, `metrics:read`, `settings:write`.
2. **`ROLE_PERMISSIONS`** mapping each `Role` to a set of permission keys (the documented matrix).
3. **`require_permission(permission: str)`** FastAPI dependency that:
   - Resolves the current authenticated user.
   - Checks membership in that role’s permission set.
   - Raises `HTTPException(403)` on failure.
   - Optionally logs the denial (user id, role, permission, path).
4. Route declarations depend on permissions, not on role names, except where object-level rules need the current user (e.g. “update self” vs “update any”).

Object-level / ownership rules (own profile, own items) stay as explicit checks in the handler or a dedicated helper; they are not replaced by the global matrix.

### Rationale

- Extending access (“managers may create users”) is a one-line matrix change, not a hunt across routers.
- Permission names document *intent* at the call site better than a list of roles.
- Option B is slightly shorter to write initially but couples endpoints to role names; every policy tweak becomes a code edit at each call site.
- Option C is what the template already drifts toward with `is_superuser` and does not meet the “easy to extend / 5 minutes to understand” bar.

### Consequences

- Small new module (policy + dependency factory) must stay the single source of role→permission mapping used by API responses (see D3).
- Call sites become declarative: `dependencies=[Depends(require_permission("users:list"))]`.
- Tests should assert both HTTP outcomes and, where useful, that the matrix helper agrees with the role.

---

## D3 — Frontend capability discovery (3B)

### Problem

The UI must hide inaccessible navigation and show Access Denied on direct navigation. If the frontend invents its own matrix, it can drift from the backend and cause confusing 403s or accidental over-exposure in the UI (UI is not security, but drift is still harmful).

### Options considered

| Option | Description |
|--------|-------------|
| A | Frontend duplicates the matrix keyed by `user.role` |
| **B (chosen)** | Backend includes `permissions: string[]` on the current-user (and optionally public user) payload |
| C | Ad-hoc `role === "admin"` checks only in components |

### Decision

Implement **Option B**.

- Compute `permissions` on the server with the **same** `ROLE_PERMISSIONS` map used by `require_permission`.
- Expose at least on `GET /users/me` (and typically on `UserPublic` so the client cache stays consistent).
- Frontend helper: `can(user, permission)` → `user.permissions.includes(permission)`.
- Route guards and sidebar use `can(...)`; they never re-implement the matrix.
- Deep links without permission render a dedicated **Access Denied** page; mutations still rely on API `403`.

### Rationale

- Single source of truth for “what can this role do?” lives in the backend policy module.
- Frontend stays dumb and resilient to matrix changes (redeploy API + refresh me).
- Option A is acceptable under a harsh timebox but we explicitly have time for the cleaner contract.
- Option C does not scale past two roles and fights the permission model in D2.

### Consequences

- OpenAPI / generated client must learn `role` and `permissions`.
- Changing the matrix automatically changes both enforcement and UI after the next `/users/me` fetch (no second TS copy to forget).
- Slightly larger JSON payload; negligible for this app.

### Security note

Returning `permissions[]` does **not** replace server checks. A user can still call the API directly; dependencies must always enforce. The list is for UX and client-side routing only.

---

## D4 — Global settings surface (4A)

### Problem

The assignment matrix includes “change global settings,” but the template only has **user** settings (profile, password, appearance). There is no first-class system configuration UI.

### Options considered

| Option | Description |
|--------|-------------|
| **A (chosen)** | Add a small **System Settings** stub (API + page), admin-only via `settings:write` |
| B | Reinterpret existing admin-only utilities (e.g. test email) as “global settings” |
| C | Cut the feature and explain the gap in `NOTES.md` |

### Decision

Implement **Option A**.

- Backend: stub endpoints (e.g. `GET`/`PATCH /settings/system`) protected by `settings:write` (admin only in the matrix). Persist lightly (DB row, JSON file, or in-memory defaults for the stub — prefer a simple persisted model if easy; in-memory/documented stub is acceptable if called out in README).
- Frontend: System Settings page + nav item gated by `settings:write`.
- User Settings (own profile) remain available to all roles under `profile:update` / authenticated self-service routes.

### Rationale

- Makes the matrix row **real and demoable** in review, not metaphorical.
- Option B overloads unrelated endpoints and confuses readers of the matrix.
- Option C is fine under time pressure; we prefer a visible stub instead.

### Consequences

- Small amount of new surface area (router + page + tests for 403/200).
- Stub must be labeled as such in README so reviewers do not expect a full configuration product.

---

## D5 — Local development workflow (5A)

### Problem

`uv` and `bun` are not installed on the host. The stack already runs successfully via Docker Compose.

### Options considered

| Option | Description |
|--------|-------------|
| **A (chosen)** | Develop and run with Docker Compose (`compose.yml` + `compose.override.yml`) |
| B | Install `uv` + `bun` and use hybrid local FastAPI/Vite + Compose for `db`/`mailpit` |

### Decision

Implement **Option A** for this project phase.

- Use `docker compose run --rm backend bash scripts/prestart.sh` for migrations/seed.
- Use `docker compose up -d` (or `watch` when iterative sync is helpful).
- Run backend tests inside the backend container / Compose test workflow.
- Frontend changes that ship inside the backend image require rebuild or the documented watch/rebuild path.

### Rationale

- Matches the already verified environment; no extra toolchain install to unblock RBAC work.
- Reviewers following README Docker instructions get the same path we used.
- Option B remains available later for faster FE HMR if desired; not required for correctness.

### Consequences

- Iteration on frontend may be slower (image rebuild) unless `docker compose watch` / volume sync is used effectively.
- Documentation should emphasize the Compose path as primary.

---

## Cross-cutting principles

1. **Server is the security boundary.** UI hiding is UX only.
2. **One policy map** feeds dependencies, `/users/me` permissions, and README matrix text.
3. **Prefer clarity over cleverness.** Small functions, explicit permission names, minimal indirection.
4. **HTTP semantics:** unauthenticated → `401` where applicable; authenticated but forbidden → `403`.
5. **Tests focus on critical allow/deny paths**, not exhaustive combinatorial coverage.
6. **Document as we go** so README setup, seed users, and the matrix stay accurate.

---

## Permission keys (canonical)

These strings are the contract between backend policy, API docs, and frontend `can()`:

| Key | Meaning |
|-----|---------|
| `users:list` | List all users |
| `users:create` | Create users |
| `users:update` | Update any user (including role assignment) |
| `users:delete` | Delete users |
| `metrics:read` | View metrics / insights stub |
| `profile:update` | Update own profile (all roles) |
| `settings:write` | View/change system (global) settings stub |

Exact role grants are listed in `PLAN.md` and must stay identical in code.

---

## Follow-ups (explicitly deferred)

- Drop `is_superuser` column entirely once all call sites and clients use `role` / permissions.
- Richer system settings persistence and audit log.
- Optional ADRs under `docs/adr/` that summarize D1–D3 for submission polish.
- Hybrid local Vite workflow (D5 Option B) if frontend iteration speed becomes a bottleneck.
