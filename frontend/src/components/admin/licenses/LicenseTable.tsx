'use client'

import { ColumnDef } from '@tanstack/react-table'
import { MoreHorizontal, ArrowUpDown, Copy, Plus } from 'lucide-react'
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
import { DataTable } from '@/components/ui/data-table'
import { License } from '@/lib/actions/admin/licenses'
import { useState } from 'react'
import { AddCreditsDialog } from './AddCreditsDialog'
import { toast } from 'sonner'

interface LicenseTableProps {
  data: License[]
  onToggleStatus: (id: string) => void
  onDelete: (id: string) => void
}

export function LicenseTable({ data, onToggleStatus, onDelete }: LicenseTableProps) {
  const [addCreditsLicense, setAddCreditsLicense] = useState<License | null>(null)

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('In Zwischenablage kopiert')
  }

  const columns: ColumnDef<License>[] = [
    {
      accessorKey: 'key',
      header: 'Lizenzschlüssel',
      cell: ({ row }) => {
        const key = row.getValue('key') as string
        return (
          <div className="flex items-center gap-2">
            <code className="text-xs bg-muted px-2 py-1 rounded">
              {key.substring(0, 24)}...
            </code>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(key)}
            >
              <Copy className="h-3 w-3" />
            </Button>
          </div>
        )
      },
    },
    {
      accessorKey: 'tenant',
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Mandant
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        const tenant = row.original.tenant
        return (
          <div>
            <div className="font-medium">{tenant?.name || 'N/A'}</div>
            <div className="text-xs text-muted-foreground">{tenant?.email || ''}</div>
          </div>
        )
      },
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
      accessorKey: 'credits_remaining',
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
        const credits = row.getValue('credits_remaining') as number
        const isLow = credits < 1000
        return (
          <div className="flex items-center gap-2">
            <span className={isLow ? 'text-red-600 font-semibold' : ''}>
              {credits.toLocaleString('de-DE')}
            </span>
            {isLow && (
              <Badge variant="destructive" className="text-xs">
                Niedrig
              </Badge>
            )}
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
      accessorKey: 'last_used_at',
      header: 'Zuletzt verwendet',
      cell: ({ row }) => {
        const lastUsed = row.getValue('last_used_at') as string | null
        return lastUsed ? (
          <div className="text-sm">
            {new Date(lastUsed).toLocaleDateString('de-DE')}
            <div className="text-xs text-muted-foreground">
              {new Date(lastUsed).toLocaleTimeString('de-DE')}
            </div>
          </div>
        ) : (
          <span className="text-muted-foreground">Nie</span>
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
        const license = row.original

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
              <DropdownMenuItem onClick={() => copyToClipboard(license.key)}>
                Lizenzschlüssel kopieren
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setAddCreditsLicense(license)}>
                <Plus className="mr-2 h-4 w-4" />
                Credits hinzufügen
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => onToggleStatus(license.id)}>
                {license.is_active ? 'Deaktivieren' : 'Aktivieren'}
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => onDelete(license.id)}
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
        searchKey="key"
        searchPlaceholder="Lizenzen suchen..."
      />

      {addCreditsLicense && (
        <AddCreditsDialog
          license={addCreditsLicense}
          open={!!addCreditsLicense}
          onOpenChange={(open) => !open && setAddCreditsLicense(null)}
        />
      )}
    </>
  )
}
