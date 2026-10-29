import { Link } from "@tanstack/react-router"
import { ShieldOff } from "lucide-react"

import { Button } from "@/components/ui/button"

const AccessDenied = () => {
  return (
    <div
      className="flex min-h-[60vh] flex-col items-center justify-center gap-4 p-6 text-center"
      data-testid="access-denied"
    >
      <ShieldOff className="size-12 text-muted-foreground" aria-hidden />
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Access Denied</h1>
        <p className="max-w-md text-muted-foreground">
          You do not have permission to view this page. If you think this is a
          mistake, contact an administrator.
        </p>
      </div>
      <Button asChild>
        <Link to="/">Back to dashboard</Link>
      </Button>
    </div>
  )
}

export default AccessDenied
