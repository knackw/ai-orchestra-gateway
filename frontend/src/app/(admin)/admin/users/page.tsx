'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { UserPlus, Search, Shield, Users as UsersIcon } from 'lucide-react'
import {
  getUsers,
  User,
  activateUser,
  deactivateUser,
  deleteUser,
} from '@/lib/actions/admin/users'
import { getTenants, Tenant } from '@/lib/actions/admin/tenants'
import { UserTable } from '@/components/admin/users/UserTable'
import { InviteUserDialog } from '@/components/admin/users/InviteUserDialog'
import { toast } from 'sonner'
import { useRouter } from 'next/navigation'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function UsersPage() {
  const router = useRouter()
  const [users, setUsers] = useState<User[]>([])
  const [filteredUsers, setFilteredUsers] = useState<User[]>([])
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [loading, setLoading] = useState(true)
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [roleFilter, setRoleFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [tenantFilter, setTenantFilter] = useState<string>('all')

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    filterUsers()
  }, [users, searchQuery, roleFilter, statusFilter, tenantFilter])

  const loadData = async () => {
    try {
      const [usersData, tenantsData] = await Promise.all([
        getUsers(),
        getTenants(),
      ])
      setUsers(usersData)
      setTenants(tenantsData)
    } catch (error) {
      toast.error('Fehler beim Laden der Daten')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const filterUsers = () => {
    let filtered = [...users]

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (u) =>
          u.email.toLowerCase().includes(query) ||
          u.name?.toLowerCase().includes(query) ||
          u.id.toLowerCase().includes(query)
      )
    }

    if (roleFilter !== 'all') {
      filtered = filtered.filter((u) => u.role === roleFilter)
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter((u) =>
        statusFilter === 'active' ? u.is_active : !u.is_active
      )
    }

    if (tenantFilter !== 'all') {
      filtered = filtered.filter((u) => u.tenant_id === tenantFilter)
    }

    setFilteredUsers(filtered)
  }

  const handleToggleStatus = async (id: string) => {
    const user = users.find((u) => u.id === id)
    if (!user) return

    try {
      if (user.is_active) {
        await deactivateUser(id)
        toast.success('Benutzer deaktiviert')
      } else {
        await activateUser(id)
        toast.success('Benutzer aktiviert')
      }
      router.refresh()
      loadData()
    } catch (error) {
      toast.error('Fehler beim Ändern des Benutzer-Status')
      console.error(error)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Möchten Sie diesen Benutzer wirklich löschen?')) {
      return
    }

    try {
      await deleteUser(id)
      toast.success('Benutzer gelöscht')
      router.refresh()
      loadData()
    } catch (error) {
      toast.error('Fehler beim Löschen des Benutzers')
      console.error(error)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-96">
          <p className="text-muted-foreground">Lädt...</p>
        </div>
      </div>
    )
  }

  const stats = {
    total: users.length,
    active: users.filter((u) => u.is_active).length,
    admins: users.filter((u) => ['admin', 'superadmin'].includes(u.role)).length,
    regular: users.filter((u) => u.role === 'user').length,
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Benutzer</h1>
          <p className="text-muted-foreground">
            Verwalten Sie Benutzer und deren Rollen
          </p>
        </div>
        <Button onClick={() => setInviteDialogOpen(true)}>
          <UserPlus className="mr-2 h-4 w-4" />
          Benutzer einladen
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <UsersIcon className="h-8 w-8 text-muted-foreground" />
              <div>
                <div className="text-2xl font-bold">{stats.total}</div>
                <div className="text-sm text-muted-foreground">Gesamt</div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="h-3 w-3 rounded-full bg-green-500" />
              <div>
                <div className="text-2xl font-bold text-green-600">{stats.active}</div>
                <div className="text-sm text-muted-foreground">Aktiv</div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <Shield className="h-8 w-8 text-blue-500" />
              <div>
                <div className="text-2xl font-bold text-blue-600">{stats.admins}</div>
                <div className="text-sm text-muted-foreground">Admins</div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <UsersIcon className="h-8 w-8 text-gray-500" />
              <div>
                <div className="text-2xl font-bold">{stats.regular}</div>
                <div className="text-sm text-muted-foreground">Benutzer</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Suche nach Email, Name oder ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={roleFilter} onValueChange={setRoleFilter}>
          <SelectTrigger className="w-full md:w-[180px]">
            <SelectValue placeholder="Rolle filtern" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Rollen</SelectItem>
            <SelectItem value="superadmin">Superadmin</SelectItem>
            <SelectItem value="admin">Admin</SelectItem>
            <SelectItem value="user">Benutzer</SelectItem>
            <SelectItem value="viewer">Viewer</SelectItem>
          </SelectContent>
        </Select>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full md:w-[180px]">
            <SelectValue placeholder="Status filtern" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Status</SelectItem>
            <SelectItem value="active">Aktiv</SelectItem>
            <SelectItem value="inactive">Inaktiv</SelectItem>
          </SelectContent>
        </Select>
        <Select value={tenantFilter} onValueChange={setTenantFilter}>
          <SelectTrigger className="w-full md:w-[200px]">
            <SelectValue placeholder="Mandant filtern" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Mandanten</SelectItem>
            {tenants.map((tenant) => (
              <SelectItem key={tenant.id} value={tenant.id}>
                {tenant.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-center gap-2">
        <Badge variant="secondary">
          {filteredUsers.length} von {users.length} Benutzern
        </Badge>
      </div>

      <UserTable
        data={filteredUsers}
        onToggleStatus={handleToggleStatus}
        onDelete={handleDelete}
        onRefresh={loadData}
      />

      <InviteUserDialog
        open={inviteDialogOpen}
        onOpenChange={setInviteDialogOpen}
        onSuccess={loadData}
      />
    </div>
  )
}
