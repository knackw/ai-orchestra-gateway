'use client'

import { ColumnDef } from '@tanstack/react-table'
import { MoreHorizontal, ArrowUpDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { DataTable } from '@/components/ui/data-table'
import { Tenant } from '@/lib/actions/admin/tenants'
import { useState } from 'react'
import { EditTenantDialog } from './EditTenantDialog'
import { TenantDetailsSheet } from './TenantDetailsSheet'

interface TenantTableProps {
  data: Tenant[]
  onDeactivate: (id: string) => void
  onDelete: (id: string) => void
}

export function TenantTable({ data, onDeactivate, onDelete }: TenantTableProps) {
  const [editingTenant, setEditingTenant] = useState<Tenant | null>(null)
  const [viewingTenant, setViewingTenant] = useState<Tenant | null>(null)

  const columns: ColumnDef<Tenant>[] = [
    {
      accessorKey: 'name',
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Name
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
    },
    {
      accessorKey: 'email',
      header: 'Email',
    },
    {
      accessorKey: 'plan',
      header: 'Plan',
      cell: ({ row }) => {
        const plan = row.getValue('plan') as string
        const colors: Record<string, string> = {
          starter: 'bg-blue-100 text-blue-800',
          professional: 'bg-purple-100 text-purple-800',
          enterprise: 'bg-orange-100 text-orange-800',
        }
        return (
          <Badge className={colors[plan] || 'bg-gray-100 text-gray-800'}>
            {plan}
          </Badge>
        )
      },
    },
    {
      accessorKey: 'credits',
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Credits
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        const credits = row.getValue('credits') as number
        const maxCredits = 100000 // Could be based on plan
        const percentage = (credits / maxCredits) * 100
        return (
          <div className="w-[200px]">
            <div className="flex justify-between text-sm mb-1">
              <span>{credits.toLocaleString('de-DE')}</span>
              <span className="text-muted-foreground">{percentage.toFixed(0)}%</span>
            </div>
            <Progress value={percentage} />
          </div>
        )
      },
    },
    {
      accessorKey: 'is_active',
      header: 'Status',
      cell: ({ row }) => {
        const isActive = row.getValue('is_active') as boolean
        return (
          <Badge variant={isActive ? 'default' : 'secondary'}>
            {isActive ? 'Aktiv' : 'Inaktiv'}
          </Badge>
        )
      },
    },
    {
      accessorKey: 'created_at',
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Erstellt
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        const date = new Date(row.getValue('created_at'))
        return date.toLocaleDateString('de-DE')
      },
    },
    {
      id: 'actions',
      cell: ({ row }) => {
        const tenant = row.original

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Menü öffnen</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Aktionen</DropdownMenuLabel>
              <DropdownMenuItem onClick={() => setViewingTenant(tenant)}>
                Details anzeigen
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setEditingTenant(tenant)}>
                Bearbeiten
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => onDeactivate(tenant.id)}>
                {tenant.is_active ? 'Deaktivieren' : 'Aktivieren'}
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => onDelete(tenant.id)}
                className="text-red-600"
              >
                Löschen
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  return (
    <>
      <DataTable
        columns={columns}
        data={data}
        searchKey="name"
        searchPlaceholder="Mandanten suchen..."
      />

      {editingTenant && (
        <EditTenantDialog
          tenant={editingTenant}
          open={!!editingTenant}
          onOpenChange={(open) => !open && setEditingTenant(null)}
        />
      )}

      {viewingTenant && (
        <TenantDetailsSheet
          tenant={viewingTenant}
          open={!!viewingTenant}
          onOpenChange={(open) => !open && setViewingTenant(null)}
        />
      )}
    </>
  )
}
