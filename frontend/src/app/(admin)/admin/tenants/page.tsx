'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Plus, Search } from 'lucide-react'
import { TenantTable } from '@/components/admin/tenants/TenantTable'
import { CreateTenantDialog } from '@/components/admin/tenants/CreateTenantDialog'
import { getTenants, deactivateTenant, activateTenant, deleteTenant, Tenant } from '@/lib/actions/admin/tenants'
import { toast } from 'sonner'
import { useRouter } from 'next/navigation'
import { Card, CardContent } from '@/components/ui/card'

export default function TenantsPage() {
  const router = useRouter()
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [filteredTenants, setFilteredTenants] = useState<Tenant[]>([])
  const [loading, setLoading] = useState(true)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  useEffect(() => {
    loadTenants()
  }, [])

  useEffect(() => {
    filterTenants()
  }, [tenants, searchQuery, statusFilter])

  const loadTenants = async () => {
    try {
      const data = await getTenants()
      setTenants(data)
    } catch (error) {
      toast.error('Fehler beim Laden der Mandanten')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const filterTenants = () => {
    let filtered = [...tenants]

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (t) =>
          t.name.toLowerCase().includes(query) ||
          t.email.toLowerCase().includes(query) ||
          t.id.toLowerCase().includes(query)
      )
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter((t) =>
        statusFilter === 'active' ? t.is_active : !t.is_active
      )
    }

    setFilteredTenants(filtered)
  }

  const handleDeactivate = async (id: string) => {
    const tenant = tenants.find((t) => t.id === id)
    if (!tenant) return

    try {
      if (tenant.is_active) {
        await deactivateTenant(id)
        toast.success('Mandant deaktiviert')
      } else {
        await activateTenant(id)
        toast.success('Mandant aktiviert')
      }
      router.refresh()
      loadTenants()
    } catch (error) {
      toast.error('Fehler beim Ändern des Mandanten-Status')
      console.error(error)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Möchten Sie diesen Mandanten wirklich löschen?')) {
      return
    }

    try {
      await deleteTenant(id)
      toast.success('Mandant gelöscht')
      router.refresh()
      loadTenants()
    } catch (error) {
      toast.error('Fehler beim Löschen des Mandanten')
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
    total: tenants.length,
    active: tenants.filter((t) => t.is_active).length,
    inactive: tenants.filter((t) => !t.is_active).length,
    totalCredits: tenants.reduce((sum, t) => sum + (t.credits || 0), 0),
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Mandanten</h1>
          <p className="text-muted-foreground">
            Verwalten Sie alle Mandanten und ihre Lizenzen
          </p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Mandant erstellen
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold">{stats.total}</div>
            <div className="text-sm text-muted-foreground">Gesamt</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-green-600">{stats.active}</div>
            <div className="text-sm text-muted-foreground">Aktiv</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-gray-600">{stats.inactive}</div>
            <div className="text-sm text-muted-foreground">Inaktiv</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold">{stats.totalCredits.toLocaleString()}</div>
            <div className="text-sm text-muted-foreground">Gesamt Credits</div>
          </CardContent>
        </Card>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Suche nach Name, Email oder ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Status filtern" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle</SelectItem>
            <SelectItem value="active">Aktiv</SelectItem>
            <SelectItem value="inactive">Inaktiv</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <TenantTable
        data={filteredTenants}
        onDeactivate={handleDeactivate}
        onDelete={handleDelete}
      />

      <CreateTenantDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onSuccess={loadTenants}
      />
    </div>
  )
}
