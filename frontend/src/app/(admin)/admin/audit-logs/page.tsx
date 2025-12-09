'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Download, Search, Filter, Eye, Calendar } from 'lucide-react'
import { getAuditLogs, AuditLog, exportAuditLogsCsv } from '@/lib/actions/admin/audit-logs'
import { getTenants, Tenant } from '@/lib/actions/admin/tenants'
import { DataTable } from '@/components/ui/data-table'
import { ColumnDef } from '@tanstack/react-table'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { toast } from 'sonner'

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [filteredLogs, setFilteredLogs] = useState<AuditLog[]>([])
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [actionFilter, setActionFilter] = useState<string>('all')
  const [tenantFilter, setTenantFilter] = useState<string>('all')
  const [dateRange, setDateRange] = useState<string>('7d')
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null)
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    filterLogs()
  }, [logs, searchQuery, actionFilter, tenantFilter, dateRange])

  const loadData = async () => {
    try {
      const [logsData, tenantsData] = await Promise.all([
        getAuditLogs({ limit: 500 }),
        getTenants(),
      ])
      setLogs(logsData)
      setTenants(tenantsData)
    } catch {
      toast.error('Fehler beim Laden der Audit-Logs')
    } finally {
      setLoading(false)
    }
  }

  const filterLogs = () => {
    let filtered = [...logs]

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (log) =>
          log.action?.toLowerCase().includes(query) ||
          log.ip_address?.toLowerCase().includes(query) ||
          JSON.stringify(log.details).toLowerCase().includes(query)
      )
    }

    if (actionFilter !== 'all') {
      filtered = filtered.filter((log) => log.action === actionFilter)
    }

    if (tenantFilter !== 'all') {
      filtered = filtered.filter((log) => log.tenant_id === tenantFilter)
    }

    if (dateRange !== 'all') {
      const now = Date.now()
      const ranges: Record<string, number> = {
        '1d': 24 * 60 * 60 * 1000,
        '7d': 7 * 24 * 60 * 60 * 1000,
        '30d': 30 * 24 * 60 * 60 * 1000,
        '90d': 90 * 24 * 60 * 60 * 1000,
      }
      const cutoff = now - (ranges[dateRange] || 0)
      filtered = filtered.filter((log) => new Date(log.created_at).getTime() >= cutoff)
    }

    setFilteredLogs(filtered)
  }

  const handleExport = async () => {
    try {
      const csv = await exportAuditLogsCsv()
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `audit-logs-${new Date().toISOString()}.csv`
      a.click()
      toast.success('Audit-Logs exportiert')
    } catch {
      toast.error('Fehler beim Exportieren')
    }
  }

  const handleViewDetails = (log: AuditLog) => {
    setSelectedLog(log)
    setDetailsDialogOpen(true)
  }

  const uniqueActions = Array.from(new Set(logs.map((log) => log.action).filter(Boolean)))

  const columns: ColumnDef<AuditLog>[] = [
    {
      accessorKey: 'created_at',
      header: 'Zeitstempel',
      cell: ({ row }) => (
        <div className="space-y-1">
          <div className="text-sm font-medium">
            {new Date(row.getValue('created_at')).toLocaleDateString('de-DE')}
          </div>
          <div className="text-xs text-muted-foreground">
            {new Date(row.getValue('created_at')).toLocaleTimeString('de-DE')}
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'tenant.name',
      header: 'Mandant',
      cell: ({ row }) => row.original.tenant?.name || '-',
    },
    {
      accessorKey: 'action',
      header: 'Aktion',
      cell: ({ row }) => {
        const action = row.getValue('action') as string
        const variant = action?.includes('delete') || action?.includes('error')
          ? 'destructive'
          : action?.includes('create') || action?.includes('success')
          ? 'default'
          : 'outline'
        return <Badge variant={variant}>{action}</Badge>
      },
    },
    {
      accessorKey: 'user_email',
      header: 'Benutzer',
      cell: ({ row }) => row.original.user_email || '-',
    },
    {
      accessorKey: 'ip_address',
      header: 'IP-Adresse',
      cell: ({ row }) => (
        <code className="text-xs bg-muted px-2 py-1 rounded">
          {row.getValue('ip_address') || '-'}
        </code>
      ),
    },
    {
      id: 'actions',
      header: 'Aktionen',
      cell: ({ row }) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => handleViewDetails(row.original)}
        >
          <Eye className="h-4 w-4" />
        </Button>
      ),
    },
  ]

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
    total: filteredLogs.length,
    today: filteredLogs.filter(
      (log) =>
        new Date(log.created_at).toDateString() === new Date().toDateString()
    ).length,
    errors: filteredLogs.filter((log) => log.action?.includes('error')).length,
    security: filteredLogs.filter(
      (log) =>
        log.action?.includes('login') ||
        log.action?.includes('auth') ||
        log.action?.includes('password')
    ).length,
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Audit-Logs</h1>
          <p className="text-muted-foreground">System-Audit-Trail und Sicherheitsereignisse</p>
        </div>
        <Button onClick={handleExport}>
          <Download className="mr-2 h-4 w-4" />
          CSV exportieren
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold">{stats.total}</div>
            <div className="text-sm text-muted-foreground">Gesamt (gefiltert)</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-blue-600">{stats.today}</div>
            <div className="text-sm text-muted-foreground">Heute</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-red-600">{stats.errors}</div>
            <div className="text-sm text-muted-foreground">Fehler</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-2xl font-bold text-orange-600">{stats.security}</div>
            <div className="text-sm text-muted-foreground">Sicherheit</div>
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Suche in Logs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={actionFilter} onValueChange={setActionFilter}>
          <SelectTrigger className="w-full md:w-[200px]">
            <SelectValue placeholder="Aktion filtern" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Aktionen</SelectItem>
            {uniqueActions.map((action) => (
              <SelectItem key={action} value={action}>
                {action}
              </SelectItem>
            ))}
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
        <Select value={dateRange} onValueChange={setDateRange}>
          <SelectTrigger className="w-full md:w-[180px]">
            <SelectValue placeholder="Zeitraum" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="1d">Letzter Tag</SelectItem>
            <SelectItem value="7d">Letzte 7 Tage</SelectItem>
            <SelectItem value="30d">Letzte 30 Tage</SelectItem>
            <SelectItem value="90d">Letzte 90 Tage</SelectItem>
            <SelectItem value="all">Alle</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {filteredLogs.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Filter className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-lg font-medium mb-2">Keine Logs gefunden</p>
            <p className="text-sm text-muted-foreground">
              Versuchen Sie, die Filter anzupassen
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">
              {filteredLogs.length} von {logs.length} Logs
            </Badge>
          </div>
          <DataTable columns={columns} data={filteredLogs} />
        </>
      )}

      <Dialog open={detailsDialogOpen} onOpenChange={setDetailsDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Audit-Log Details</DialogTitle>
          </DialogHeader>
          {selectedLog && (
            <div className="space-y-4">
              <div>
                <div className="text-sm font-medium text-muted-foreground">Zeitstempel</div>
                <div className="text-sm">
                  {new Date(selectedLog.created_at).toLocaleString('de-DE')}
                </div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground">Aktion</div>
                <Badge variant="outline">{selectedLog.action}</Badge>
              </div>
              {selectedLog.tenant && (
                <div>
                  <div className="text-sm font-medium text-muted-foreground">Mandant</div>
                  <div className="text-sm">{selectedLog.tenant.name}</div>
                </div>
              )}
              {selectedLog.user_email && (
                <div>
                  <div className="text-sm font-medium text-muted-foreground">Benutzer</div>
                  <div className="text-sm">{selectedLog.user_email}</div>
                </div>
              )}
              {selectedLog.ip_address && (
                <div>
                  <div className="text-sm font-medium text-muted-foreground">IP-Adresse</div>
                  <code className="text-sm bg-muted px-2 py-1 rounded">
                    {selectedLog.ip_address}
                  </code>
                </div>
              )}
              <div>
                <div className="text-sm font-medium text-muted-foreground mb-2">Details</div>
                <pre className="text-xs bg-muted p-4 rounded-lg overflow-x-auto">
                  {JSON.stringify(selectedLog.details, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
