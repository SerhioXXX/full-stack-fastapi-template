import type { UserPublic } from "@/client"

/** Permission keys — keep in sync with backend `app.core.rbac.Permission`. */
export const Permission = {
  USERS_LIST: "users:list",
  USERS_CREATE: "users:create",
  USERS_UPDATE: "users:update",
  USERS_DELETE: "users:delete",
  METRICS_READ: "metrics:read",
  PROFILE_UPDATE: "profile:update",
  SETTINGS_WRITE: "settings:write",
} as const

export type PermissionKey = (typeof Permission)[keyof typeof Permission]

export function can(
  user: Pick<UserPublic, "permissions"> | null | undefined,
  permission: PermissionKey | string,
): boolean {
  return Boolean(user?.permissions?.includes(permission))
}
