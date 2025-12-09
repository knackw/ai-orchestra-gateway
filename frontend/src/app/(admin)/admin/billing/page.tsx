'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { getCreditHistory, manualCreditTopUp, CreditTransaction } from '@/lib/actions/admin/billing'
import { getTenants, Tenant } from '@/lib/actions/admin/tenants'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { toast } from 'sonner'
import { DataTable } from '@/components/ui/data-table'
import { ColumnDef } from '@tanstack/react-table'
import { Badge } from '@/components/ui/badge'

export default function AdminBillingPage() {
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [creditHistory, setCreditHistory] = useState<CreditTransaction[]>([])
  const [loading, setLoading] = useState(true)
  const [formData, setFormData] = useState({
    tenant_id: '',
    amount: 1000,
    note: '',
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [tenantsData, historyData] = await Promise.all([
        getTenants(),
        getCreditHistory(),
      ])
      setTenants(tenantsData)
      setCreditHistory(historyData)
    } catch {
      toast.error('Fehler beim Laden der Daten')
    } finally {
      setLoading(false)
    }
  }

  const handleTopUp = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await manualCreditTopUp(formData)
      toast.success('Credits erfolgreich hinzugefügt')
      loadData()
      setFormData({ tenant_id: '', amount: 1000, note: '' })
    } catch {
      toast.error('Fehler beim Hinzufügen der Credits')
    }
  }

  const columns: ColumnDef<CreditTransaction>[] = [
    {
      accessorKey: 'created_at',
      header: 'Datum',
      cell: ({ row }) => new Date(row.getValue('created_at')).toLocaleDateString('de-DE'),
    },
    {
      accessorKey: 'tenant.name',
      header: 'Mandant',
      cell: ({ row }) => row.original.tenant?.name || '-',
    },
    {
      accessorKey: 'amount',
      header: 'Betrag',
      cell: ({ row }) => {
        const amount = row.getValue('amount') as number
        return <span className={amount > 0 ? 'text-green-600' : 'text-red-600'}>
          {amount > 0 ? '+' : ''}{amount.toLocaleString('de-DE')}
        </span>
      },
    },
    {
      accessorKey: 'type',
      header: 'Typ',
      cell: ({ row }) => <Badge variant="outline">{row.getValue('type')}</Badge>,
    },
    {
      accessorKey: 'note',
      header: 'Notiz',
      cell: ({ row }) => row.getValue('note') || '-',
    },
  ]

  if (loading) {
    return <div className="container mx-auto p-6">Lädt...</div>
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Abrechnungsverwaltung</h1>
        <p className="text-muted-foreground">Verwalten Sie Rechnungen und Zahlungen</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Manuelle Credit-Aufladung</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleTopUp} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="tenant">Mandant</Label>
                <Select
                  value={formData.tenant_id}
                  onValueChange={(value) => setFormData({ ...formData, tenant_id: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Mandant auswählen" />
                  </SelectTrigger>
                  <SelectContent>
                    {tenants.map((tenant) => (
                      <SelectItem key={tenant.id} value={tenant.id}>
                        {tenant.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="amount">Betrag (Credits)</Label>
                <Input
                  id="amount"
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: parseInt(e.target.value) })}
                  min={1}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="note">Notiz (optional)</Label>
                <Textarea
                  id="note"
                  value={formData.note}
                  onChange={(e) => setFormData({ ...formData, note: e.target.value })}
                  placeholder="Grund für die Aufladung..."
                />
              </div>
              <Button type="submit" className="w-full">
                Credits hinzufügen
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Statistiken</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Gesamt Credits vergeben</span>
              <span className="text-2xl font-bold">
                {creditHistory
                  .filter((t) => t.amount > 0)
                  .reduce((sum, t) => sum + t.amount, 0)
                  .toLocaleString('de-DE')}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Transaktionen heute</span>
              <span className="text-2xl font-bold">
                {creditHistory.filter((t) => {
                  const today = new Date().toDateString()
                  return new Date(t.created_at).toDateString() === today
                }).length}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Credit-Historie</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={creditHistory} searchKey="type" />
        </CardContent>
      </Card>
    </div>
  )
}
