'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Plus, Search, Filter } from 'lucide-react'
import {
  getLicenses,
  License,
  activateLicense,
  deactivateLicense,
  deleteLicense,
} from '@/lib/actions/admin/licenses'
import { getTenants, Tenant } from '@/lib/actions/admin/tenants'
import { LicenseTable } from '@/components/admin/licenses/LicenseTable'
import { CreateLicenseDialog } from '@/components/admin/licenses/CreateLicenseDialog'
import { toast } from 'sonner'
import { useRouter } from 'next/navigation'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function LicensesPage() {
  const router = useRouter()
  const [licenses, setLicenses] = useState<License[]>([])
  const [filteredLicenses, setFilteredLicenses] = useState<License[]>([])
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [loading, setLoading] = useState(true)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [tenantFilter, setTenantFilter] = useState<string>('all')

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    filterLicenses()
  }, [licenses, searchQuery, statusFilter, tenantFilter])

  const loadData = async () => {
    try {
      const [licensesData, tenantsData] = await Promise.all([
        getLicenses(),
        getTenants(),
      ])
      setLicenses(licensesData)
      setTenants(tenantsData)
    } catch (error) {
      toast.error('Fehler beim Laden der Daten')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const filterLicenses = () => {
    let filtered = [...licenses]

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (l) =>
          l.name.toLowerCase().includes(query) ||
          l.id.toLowerCase().includes(query) ||
          l.api_key?.toLowerCase().includes(query)
      )
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter((l) =>
        statusFilter === 'active' ? l.is_active : !l.is_active
      )
    }

    if (tenantFilter !== 'all') {
      filtered = filtered.filter((l) => l.tenant_id === tenantFilter)
    }

    setFilteredLicenses(filtered)
  }

  const handleToggleStatus = async (id: string) => {
    const license = licenses.find((l) => l.id === id)
    if (!license) return

    try {
      if (license.is_active) {
        await deactivateLicense(id)
        toast.success('Lizenz deaktiviert')
      } else {
        await activateLicense(id)
        toast.success('Lizenz aktiviert')
      }
      router.refresh()
      loadData()
    } catch (error) {
      toast.error('Fehler beim Ändern des Lizenz-Status')
      console.error(error)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Möchten Sie diese Lizenz wirklich löschen?')) {
      return
    }

    try {
      await deleteLicense(id)
      toast.success('Lizenz gelöscht')
      router.refresh()
      loadData()
    } catch (error) {
      toast.error('Fehler beim Löschen der Lizenz')
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
    total: licenses.length,
    active: licenses.filter((l) => l.is_active).length,
    inactive: licenses.filter((l) => !l.is_active).length,
    expiringSoon: licenses.filter((l) => {
      if (!l.expires_at) return false
      const daysUntilExpiry = Math.floor(
        (new Date(l.expires_at).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
      )
      return daysUntilExpiry > 0 && daysUntilExpiry <= 30
    }).length,
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Lizenzen</h1>
          <p className="text-muted-foreground">
            Verwalten Sie alle API-Lizenzen und Credits
          </p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Lizenz erstellen
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
            <div className="text-2xl font-bold text-orange-600">{stats.expiringSoon}</div>
            <div className="text-sm text-muted-foreground">Läuft bald ab</div>
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Suche nach Name, ID oder API-Key..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
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

      {filteredLicenses.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Filter className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-lg font-medium mb-2">Keine Lizenzen gefunden</p>
            <p className="text-sm text-muted-foreground">
              Versuchen Sie, die Filter anzupassen
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">
              {filteredLicenses.length} von {licenses.length} Lizenzen
            </Badge>
          </div>
          <LicenseTable
            data={filteredLicenses}
            onToggleStatus={handleToggleStatus}
            onDelete={handleDelete}
          />
        </>
      )}

      <CreateLicenseDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onSuccess={loadData}
      />
    </div>
  )
}
