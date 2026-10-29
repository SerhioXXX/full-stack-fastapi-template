# RBAC Implementation Plan

This plan implements Role-Based Access Control (RBAC) on top of the [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template), as specified in `TASK.md`.

Architecture choices are documented in [`DECISION.md`](./DECISION.md).

**Status:** Local Docker stack is running (`http://localhost:8000`). Implementation not started.

**Chosen options:** 1A (role column), 2A (permission dependencies), 3B (`permissions[]` from `/users/me`), 4A (system settings stub), 5A (Docker Compose workflow).

---

## Permission Matrix (source of truth)

| Action | Permission key | admin | manager | member |
|--------|----------------|-------|---------|--------|
| List all users | `users:list` | ✓ | ✓ | ✗ |
| Create user | `users:create` | ✓ | ✗ | ✗ |
| Update any user / assign roles | `users:update` | ✓ | ✗ | ✗ |
| Delete user | `users:delete` | ✓ | ✗ | ✗ |
| View metrics | `metrics:read` | ✓ | ✓ | ✗ |
| Update own profile | `profile:update` | ✓ | ✓ | ✓ |
| View / change global (system) settings | `settings:write` | ✓ | ✗ | ✗ |

Notes:

- Own-profile read/update remains available to every authenticated active user (`GET/PATCH /users/me`).
- `is_superuser` is derived from `role == admin` for backward compatibility during migration; `role` is the authority.
- Backend enforces every check. Frontend only hides UI and shows Access Denied for better UX.

---

## Phase 0 — Baseline (done)

- [x] Clone / open the template repository
- [x] Start stack with Docker Compose (`db`, `backend`, `proxy`, `mailpit`, `adminer`)
- [x] Verify health, docs, UI, and admin login (`admin@example.com` / `changethis`)
- [x] Capture decisions in `DECISION.md` and this plan

---

## Phase 1 — Backend domain model ✅

1. [x] Add `Role` enum: `admin` | `manager` | `member`.
2. [x] Add `User.role` column (string/enum, indexed, non-null, default `member`).
3. [x] Keep `is_superuser` temporarily; treat it as derived via `sync_role_and_superuser`.
4. [x] Alembic migration `b7e3a1c94d20_add_user_role` with backfill.
5. [x] Update schemas (`UserCreate`, `UserUpdate`, `UserPublic` via `UserBase`) to include `role`.
6. [x] Update seed / `initial_data` so the first superuser is `admin`.

**Deliverable:** Migrated schema; existing admin logs in with `role=admin`. Done.

---

## Phase 2 — Authorization policy layer ✅

1. [x] Policy module `backend/app/core/rbac.py` (`Permission`, `ROLE_PERMISSIONS`, helpers).
2. [x] `require_permission(...)` in `deps.py` with warning-level denial logging.
3. [x] Replaced superuser gates on users / utils / login HTML recovery with permission deps.
4. [x] Object-level: `GET /users/{id}` uses `users:list`; self-delete blocked for `Role.ADMIN`.
5. [x] Items ownership still uses legacy `is_superuser` (out of RBAC surface for now).
6. [x] Matrix unit tests in `tests/core/test_rbac.py`.

**Deliverable:** Consistent permission dependency pattern. Done.

---

## Phase 3 — Protect API surface ✅

| Area | Endpoint | Permission |
|------|----------|------------|
| List users | `GET /users/` | `users:list` |
| Create user | `POST /users/` | `users:create` (admin may set `role`) |
| Update / delete user | `PATCH/DELETE /users/{id}` | `users:update` / `users:delete` |
| Own profile | `GET/PATCH /users/me`, password | authenticated / `profile:update` |
| Metrics | `GET /metrics/` | `metrics:read` (live counts stub) |
| System settings | `GET/PATCH /settings/system` | `settings:write` (in-memory stub) |

Also done:

- [x] Public signup always forces `role=member` (ignores elevated payload fields).
- [x] Public routes (login, register, recovery, health) unchanged.
- [x] Items ownership still legacy `is_superuser`.
- [x] API tests for metrics/settings allow/deny + role create/signup hardening.

**Deliverable:** Unauthorized callers get `403`; authorized callers succeed. Done.

---

## Phase 4 — Seed test users ✅

Idempotent seed in `backend/app/core/db.py` (`init_db` / `prestart`):

| Email | Password | Role | Purpose |
|-------|----------|------|---------|
| `admin@example.com` (`FIRST_SUPERUSER`) | `changethis` | admin | Full access |
| `manager@example.com` | `changethis` | manager | List users + metrics; no create/settings |
| `member@example.com` | `changethis` | member | Own profile only for sensitive areas |

- [x] Create-if-missing; sync role if account already exists with wrong role.
- [x] Covered by `tests/core/test_seed_users.py`.
- [ ] Document in README (Phase 7).

**Deliverable:** Three ready accounts after `prestart` / seed. Done.

---

## Phase 5 — Frontend RBAC ✅

1. [x] Regenerated OpenAPI client (`frontend/openapi.json` + `bun run generate-client`).
2. [x] `UserPublic` includes `role` + `permissions[]` (server-populated from `ROLE_PERMISSIONS`).
3. [x] Frontend `can()` helper in `frontend/src/lib/permissions.ts`.
4. [x] Sidebar: Admin / Metrics / System Settings gated by permissions.
5. [x] Route guards → `/forbidden` (Access Denied) for admin, metrics, system-settings.
6. [x] Admin UI: role select; Add User / edit / delete gated by permissions.
7. [x] Pages: `/metrics`, `/system-settings`, `/forbidden`.

**Deliverable:** UI matches the matrix; deep links show Access Denied; API remains the gate. Done.

---

## Phase 6 — Tests ✅

Focused suite in `backend/tests/api/routes/test_rbac.py` (+ helpers in `tests/utils/user.py`):

1. [x] Member cannot `GET /users/` → `403`
2. [x] Manager can `GET /users/` → `200`, cannot `POST /users/` → `403`
3. [x] Admin can create user + access system settings
4. [x] Member can update own profile; cannot update another user → `403`
5. [x] Manager can `GET /metrics/`; member cannot → `403`
6. [x] `/users/me` `permissions[]` matches `ROLE_PERMISSIONS` for every role
7. [x] Manager cannot access system settings → `403`
8. [x] `conftest` re-seeds demo users after teardown (shared local DB stays usable)

**Deliverable:** Critical allow/deny paths green. Done (`15 passed` with related suites).

---

## Phase 7 — Documentation & submission

Update root `README.md` (or a clear RBAC section) with:

- How to run locally (Docker Compose path we use)
- Permission matrix
- Short architecture explanation (where checks live, how roles are stored, how frontend gets capabilities)
- How to seed / use test users
- How to run migrations and tests

Optional extras (do if time allows; not required to “finish”):

- `NOTES.md` — trade-offs and follow-ups
- 1–2 ADRs (can largely point at `DECISION.md`)
- Mermaid diagram of authn → authz → handler
- Logging of denied access (if not already in Phase 2)

Submission checklist from `TASK.md`:

- [ ] Working RBAC code
- [ ] Backend tests for critical authz scenarios
- [ ] Updated README
- [ ] PR or repo link with commit history
- [ ] Optional `NOTES.md`

---

## Suggested implementation order

```text
Phase 1 (model + migration)
    → Phase 2 (policy + require_permission)
    → Phase 3 (wire endpoints + stubs)
    → Phase 4 (seed users)
    → Phase 6 (backend tests)     # can start as soon as Phase 3 is stable
    → Phase 5 (frontend + Access Denied)
    → Phase 7 (README / NOTES)
```

Frontend (Phase 5) depends on `role` + `permissions` in the me/user response; regenerate client after Phase 3.

---

## Out of scope (unless explicitly expanded later)

- Full Casbin/Oso or external policy engine
- Multi-role users / custom permission grants per user
- Fine-grained item ACL redesign beyond existing owner/superuser behavior
- Comprehensive E2E Playwright coverage for every role (manual smoke + backend tests are enough)
- Production secret hardening beyond documenting `.env` defaults

---

## Local run reference (Phase 5A)

```bash
docker compose run --rm backend bash scripts/prestart.sh
docker compose up -d
```

- App: http://localhost:8000  
- API docs: http://localhost:8000/docs  
- Adminer: http://localhost:8080  
- Mailpit: http://localhost:8025  

After code changes that affect the backend image or built frontend, rebuild as needed (`docker compose up -d --build` or `docker compose watch` for sync workflows).
