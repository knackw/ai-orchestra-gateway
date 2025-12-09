'use client'

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Tenant } from '@/lib/actions/admin/tenants'

interface TenantDetailsSheetProps {
  tenant: Tenant
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function TenantDetailsSheet({ tenant, open, onOpenChange }: TenantDetailsSheetProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-[400px] sm:w-[540px]">
        <SheetHeader>
          <SheetTitle>{tenant.name}</SheetTitle>
          <SheetDescription>Mandanten-Details und Informationen</SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          <div>
            <h3 className="text-sm font-medium mb-3">Grundinformationen</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Firmenname</span>
                <span className="text-sm font-medium">{tenant.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Email</span>
                <span className="text-sm font-medium">{tenant.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Status</span>
                <Badge variant={tenant.is_active ? 'default' : 'secondary'}>
                  {tenant.is_active ? 'Aktiv' : 'Inaktiv'}
                </Badge>
              </div>
            </div>
          </div>

          <Separator />

          <div>
            <h3 className="text-sm font-medium mb-3">Plan & Credits</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Plan</span>
                <Badge>{tenant.plan}</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Verfügbare Credits</span>
                <span className="text-sm font-medium">
                  {tenant.credits.toLocaleString('de-DE')}
                </span>
              </div>
            </div>
          </div>

          <Separator />

          <div>
            <h3 className="text-sm font-medium mb-3">Zeitstempel</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Erstellt am</span>
                <span className="text-sm font-medium">
                  {new Date(tenant.created_at).toLocaleString('de-DE')}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Aktualisiert am</span>
                <span className="text-sm font-medium">
                  {new Date(tenant.updated_at).toLocaleString('de-DE')}
                </span>
              </div>
            </div>
          </div>

          <Separator />

          <div>
            <h3 className="text-sm font-medium mb-3">Statistiken</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border p-3">
                <div className="text-2xl font-bold">0</div>
                <div className="text-xs text-muted-foreground">Aktive Lizenzen</div>
              </div>
              <div className="rounded-lg border p-3">
                <div className="text-2xl font-bold">0</div>
                <div className="text-xs text-muted-foreground">Benutzer</div>
              </div>
              <div className="rounded-lg border p-3">
                <div className="text-2xl font-bold">0</div>
                <div className="text-xs text-muted-foreground">API Aufrufe</div>
              </div>
              <div className="rounded-lg border p-3">
                <div className="text-2xl font-bold">€0</div>
                <div className="text-xs text-muted-foreground">Umsatz gesamt</div>
              </div>
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
