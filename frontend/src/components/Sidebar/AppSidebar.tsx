import { BarChart3, Briefcase, Home, Settings2, Users } from "lucide-react"

import { SidebarAppearance } from "@/components/Common/Appearance"
import { Logo } from "@/components/Common/Logo"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import { can, Permission } from "@/lib/permissions"
import { type Item, Main } from "./Main"
import { User } from "./User"

const baseItems: Item[] = [
  { icon: Home, title: "Dashboard", path: "/" },
  { icon: Briefcase, title: "Items", path: "/items" },
]

export function AppSidebar() {
  const { user: currentUser } = useAuth()

  const items: Item[] = [...baseItems]
  if (can(currentUser, Permission.USERS_LIST)) {
    items.push({ icon: Users, title: "Admin", path: "/admin" })
  }
  if (can(currentUser, Permission.METRICS_READ)) {
    items.push({ icon: BarChart3, title: "Metrics", path: "/metrics" })
  }
  if (can(currentUser, Permission.SETTINGS_WRITE)) {
    items.push({
      icon: Settings2,
      title: "System Settings",
      path: "/system-settings",
    })
  }

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-4 py-6 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:items-center">
        <Logo variant="responsive" />
      </SidebarHeader>
      <SidebarContent>
        <Main items={items} />
      </SidebarContent>
      <SidebarFooter>
        <SidebarAppearance />
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
