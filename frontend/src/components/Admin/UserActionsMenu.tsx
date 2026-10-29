import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { UserPublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import useAuth from "@/hooks/useAuth"
import { can, Permission } from "@/lib/permissions"
import DeleteUser from "./DeleteUser"
import EditUser from "./EditUser"

interface UserActionsMenuProps {
  user: UserPublic
}

export const UserActionsMenu = ({ user }: UserActionsMenuProps) => {
  const [open, setOpen] = useState(false)
  const { user: currentUser } = useAuth()

  const canUpdate = can(currentUser, Permission.USERS_UPDATE)
  const canDelete = can(currentUser, Permission.USERS_DELETE)

  if (user.id === currentUser?.id || (!canUpdate && !canDelete)) {
    return null
  }

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {canUpdate && (
          <EditUser user={user} onSuccess={() => setOpen(false)} />
        )}
        {canDelete && (
          <DeleteUser id={user.id} onSuccess={() => setOpen(false)} />
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
