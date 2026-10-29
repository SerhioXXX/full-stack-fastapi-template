import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { SettingsService, UsersService } from "@/client"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { can, Permission } from "@/lib/permissions"
import { handleError } from "@/utils"

const formSchema = z.object({
  site_name: z.string().min(1, { message: "Site name is required" }).max(255),
  maintenance_mode: z.boolean(),
  support_email: z
    .string()
    .email({ message: "Invalid email address" })
    .optional()
    .or(z.literal("")),
})

type FormData = z.infer<typeof formSchema>

export const Route = createFileRoute("/_layout/system-settings")({
  component: SystemSettingsPage,
  beforeLoad: async () => {
    const { data: user } = await UsersService.readUserMe()
    if (!can(user, Permission.SETTINGS_WRITE)) {
      throw redirect({ to: "/forbidden" })
    }
  },
  head: () => ({
    meta: [{ title: "System Settings - FastAPI Template" }],
  }),
})

function SystemSettingsPage() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data, isLoading } = useQuery({
    queryKey: ["system-settings"],
    queryFn: async () => (await SettingsService.readSystemSettings()).data,
  })

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      site_name: "",
      maintenance_mode: false,
      support_email: "",
    },
  })

  useEffect(() => {
    if (data) {
      form.reset({
        site_name: data.site_name,
        maintenance_mode: data.maintenance_mode,
        support_email: data.support_email ?? "",
      })
    }
  }, [data, form])

  const mutation = useMutation({
    mutationFn: (body: FormData) =>
      SettingsService.patchSystemSettings({
        body: {
          site_name: body.site_name,
          maintenance_mode: body.maintenance_mode,
          support_email: body.support_email || null,
        },
      }),
    onSuccess: () => {
      showSuccessToast("System settings updated")
      queryClient.invalidateQueries({ queryKey: ["system-settings"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">System Settings</h1>
        <p className="text-muted-foreground">
          Global application settings (admin-only stub; stored in memory)
        </p>
      </div>

      {isLoading && (
        <p className="text-muted-foreground">Loading settings…</p>
      )}

      {!isLoading && (
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit((values) => mutation.mutate(values))}
            className="flex max-w-lg flex-col gap-4"
          >
            <FormField
              control={form.control}
              name="site_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Site name</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="support_email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Support email</FormLabel>
                  <FormControl>
                    <Input type="email" placeholder="support@example.com" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="maintenance_mode"
              render={({ field }) => (
                <FormItem className="flex items-center gap-3 space-y-0">
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                  <FormLabel className="font-normal">Maintenance mode</FormLabel>
                </FormItem>
              )}
            />

            <div className="flex gap-2">
              <LoadingButton type="submit" loading={mutation.isPending}>
                Save
              </LoadingButton>
              <Button
                type="button"
                variant="outline"
                onClick={() => data && form.reset({
                  site_name: data.site_name,
                  maintenance_mode: data.maintenance_mode,
                  support_email: data.support_email ?? "",
                })}
              >
                Reset
              </Button>
            </div>
          </form>
        </Form>
      )}
    </div>
  )
}
