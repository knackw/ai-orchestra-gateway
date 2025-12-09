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
import { DataTable } from '@/components/ui/data-table'
import { User } from '@/lib/actions/admin/users'
import { useState } from 'react'
import { EditUserDialog } from './EditUserDialog'

interface UserTableProps {
  data: User[]
  onToggleStatus: (id: string) => void
  onDelete: (id: string) => void
}

export function UserTable({ data, onToggleStatus, onDelete }: UserTableProps) {
  const [editingUser, setEditingUser] = useState<User | null>(null)

  const getRoleBadgeColor = (role: string) => {
    const colors: Record<string, string> = {
      admin: 'bg-red-100 text-red-800',
      user: 'bg-blue-100 text-blue-800',
      viewer: 'bg-gray-100 text-gray-800',
    }
    return colors[role] || 'bg-gray-100 text-gray-800'
  }

  const columns: ColumnDef<User>[] = [
    {
      accessorKey: 'email',
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Email
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
    },
    {
      accessorKey: 'full_name',
      header: 'Name',
      cell: ({ row }) => {
        const name = row.getValue('full_name') as string | null
        return name || <span className="text-muted-foreground">-</span>
      },
    },
    {
      accessorKey: 'role',
      header: 'Rolle',
      cell: ({ row }) => {
        const role = row.getValue('role') as string
        return (
          <Badge className={getRoleBadgeColor(role)}>
            {role === 'admin' ? 'Admin' : role === 'user' ? 'Benutzer' : 'Betrachter'}
          </Badge>
        )
      },
    },
    {
      accessorKey: 'tenant',
      header: 'Mandant',
      cell: ({ row }) => {
        const tenant = row.original.tenant
        return tenant ? (
          <span>{tenant.name}</span>
        ) : (
          <span className="text-muted-foreground">Kein Mandant</span>
        )
      },
    },
    {
      accessorKey: 'last_login_at',
      header: 'Letzter Login',
      cell: ({ row }) => {
        const lastLogin = row.getValue('last_login_at') as string | null
        return lastLogin ? (
          <div className="text-sm">
            {new Date(lastLogin).toLocaleDateString('de-DE')}
            <div className="text-xs text-muted-foreground">
              {new Date(lastLogin).toLocaleTimeString('de-DE')}
            </div>
          </div>
        ) : (
          <span className="text-muted-foreground">Nie</span>
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
        const user = row.original

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
              <DropdownMenuItem onClick={() => setEditingUser(user)}>
                Bearbeiten
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => onToggleStatus(user.id)}>
                {user.is_active ? 'Deaktivieren' : 'Aktivieren'}
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => onDelete(user.id)}
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
        searchKey="email"
        searchPlaceholder="Benutzer suchen..."
      />

      {editingUser && (
        <EditUserDialog
          user={editingUser}
          open={!!editingUser}
          onOpenChange={(open) => !open && setEditingUser(null)}
        />
      )}
    </>
  )
}
