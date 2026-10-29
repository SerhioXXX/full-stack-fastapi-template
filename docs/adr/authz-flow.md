# Authorization check flow

```mermaid
flowchart TD
    A[Client request + JWT] --> B{Valid token?}
    B -->|no| C[401 / 403 credentials]
    B -->|yes| D[Load User from DB]
    D --> E{Active user?}
    E -->|no| F[400 Inactive user]
    E -->|yes| G{Route has require_permission?}
    G -->|no| H[Handler - e.g. public or self-service only]
    G -->|yes| I{permission in ROLE_PERMISSIONS role}
    I -->|no| J[Log WARNING + 403]
    I -->|yes| K[Handler]
    H --> L[Response]
    K --> L
```

Protected examples:

- `GET /api/v1/users/` → `users:list`
- `POST /api/v1/users/` → `users:create`
- `GET /api/v1/metrics/` → `metrics:read`
- `GET/PATCH /api/v1/settings/system` → `settings:write`
