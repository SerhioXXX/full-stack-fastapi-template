import { useQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"

import { MetricsService, UsersService } from "@/client"
import { can, Permission } from "@/lib/permissions"

export const Route = createFileRoute("/_layout/metrics")({
  component: MetricsPage,
  beforeLoad: async () => {
    const { data: user } = await UsersService.readUserMe()
    if (!can(user, Permission.METRICS_READ)) {
      throw redirect({ to: "/forbidden" })
    }
  },
  head: () => ({
    meta: [{ title: "Metrics - FastAPI Template" }],
  }),
})

function MetricsPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["metrics"],
    queryFn: async () => (await MetricsService.readMetrics()).data,
  })

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Metrics</h1>
        <p className="text-muted-foreground">
          Lightweight insights for admins and managers
        </p>
      </div>

      {isLoading && <p className="text-muted-foreground">Loading metrics…</p>}
      {isError && (
        <p className="text-destructive">Could not load metrics.</p>
      )}
      {data && (
        <div className="grid gap-4 sm:grid-cols-3">
          <MetricCard label="Total users" value={data.total_users} />
          <MetricCard label="Active users" value={data.active_users} />
          <MetricCard label="Total items" value={data.total_items} />
        </div>
      )}
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border bg-card p-6">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-2 text-3xl font-semibold tracking-tight">{value}</p>
    </div>
  )
}
