'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { ColumnDef } from '@tanstack/react-table'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  getModelPricing,
  ModelPricing,
  updatePricing,
  exportPricingCsv,
} from '@/lib/actions/admin/pricing'
import { DollarSign, Download, Edit, TrendingUp } from 'lucide-react'
import { toast } from 'sonner'
import { Loader2 } from 'lucide-react'

export default function PricingPage() {
  const [pricing, setPricing] = useState<ModelPricing[]>([])
  const [loading, setLoading] = useState(true)
  const [editingPricing, setEditingPricing] = useState<ModelPricing | null>(null)
  const [editFormData, setEditFormData] = useState({
    markup_percentage: 0,
  })

  useEffect(() => {
    loadPricing()
  }, [])

  const loadPricing = async () => {
    try {
      const data = await getModelPricing()
      setPricing(data)
    } catch (error) {
      toast.error('Fehler beim Laden der Preise')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (item: ModelPricing) => {
    setEditingPricing(item)
    setEditFormData({
      markup_percentage: item.markup_percentage,
    })
  }

  const handleSave = async () => {
    if (!editingPricing) return

    setLoading(true)
    try {
      await updatePricing(editingPricing.id, {
        markup_percentage: editFormData.markup_percentage,
      })
      toast.success('Preis erfolgreich aktualisiert')
      setEditingPricing(null)
      loadPricing()
    } catch (error) {
      toast.error('Fehler beim Aktualisieren')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    try {
      const csv = await exportPricingCsv()
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `model-pricing-${new Date().toISOString()}.csv`
      a.click()
      toast.success('CSV erfolgreich exportiert')
    } catch (error) {
      toast.error('Fehler beim Exportieren')
      console.error(error)
    }
  }

  const columns: ColumnDef<ModelPricing>[] = [
    {
      accessorKey: 'model_name',
      header: 'Modell',
      cell: ({ row }) => {
        return (
          <div>
            <div className="font-medium">{row.original.model_name}</div>
            <div className="text-xs text-muted-foreground">
              {row.original.provider_name}
            </div>
          </div>
        )
      },
    },
    {
      accessorKey: 'input_price_per_1k_tokens',
      header: 'Input Basis (€/1k)',
      cell: ({ row }) => {
        const price = row.getValue('input_price_per_1k_tokens') as number
        return <span className="font-mono">€{price.toFixed(6)}</span>
      },
    },
    {
      accessorKey: 'output_price_per_1k_tokens',
      header: 'Output Basis (€/1k)',
      cell: ({ row }) => {
        const price = row.getValue('output_price_per_1k_tokens') as number
        return <span className="font-mono">€{price.toFixed(6)}</span>
      },
    },
    {
      accessorKey: 'markup_percentage',
      header: 'Markup',
      cell: ({ row }) => {
        const markup = row.getValue('markup_percentage') as number
        return (
          <Badge variant="outline" className="font-mono">
            +{markup.toFixed(1)}%
          </Badge>
        )
      },
    },
    {
      accessorKey: 'effective_input_price',
      header: 'Effektiv Input (€/1k)',
      cell: ({ row }) => {
        const price = row.getValue('effective_input_price') as number
        return (
          <span className="font-mono font-semibold text-green-600">
            €{price.toFixed(6)}
          </span>
        )
      },
    },
    {
      accessorKey: 'effective_output_price',
      header: 'Effektiv Output (€/1k)',
      cell: ({ row }) => {
        const price = row.getValue('effective_output_price') as number
        return (
          <span className="font-mono font-semibold text-green-600">
            €{price.toFixed(6)}
          </span>
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
      id: 'actions',
      cell: ({ row }) => {
        return (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleEdit(row.original)}
          >
            <Edit className="h-4 w-4" />
          </Button>
        )
      },
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

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <DollarSign className="h-8 w-8" />
            Model Pricing Management
          </h1>
          <p className="text-muted-foreground mt-2">
            Verwalten Sie Preise und Markup für alle Modelle
          </p>
        </div>
        <Button onClick={handleExport}>
          <Download className="mr-2 h-4 w-4" />
          CSV Exportieren
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Gesamt Modelle</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pricing.length}</div>
            <p className="text-xs text-muted-foreground">
              {pricing.filter((p) => p.is_active).length} aktiv
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Durchschn. Markup</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(
                pricing.reduce((acc, p) => acc + p.markup_percentage, 0) /
                pricing.length
              ).toFixed(1)}
              %
            </div>
            <p className="text-xs text-muted-foreground">
              Über alle Modelle
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Provider</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Set(pricing.map((p) => p.provider_name)).size}
            </div>
            <p className="text-xs text-muted-foreground">
              Verschiedene Provider
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Pricing Table */}
      <DataTable
        columns={columns}
        data={pricing}
        searchKey="model_name"
        searchPlaceholder="Modelle suchen..."
      />

      {/* Edit Dialog */}
      <Dialog open={!!editingPricing} onOpenChange={(open) => !open && setEditingPricing(null)}>
        <DialogContent className="sm:max-w-[525px]">
          <DialogHeader>
            <DialogTitle>Pricing bearbeiten</DialogTitle>
            <DialogDescription>
              Aktualisieren Sie den Markup-Prozentsatz für dieses Modell
            </DialogDescription>
          </DialogHeader>
          {editingPricing && (
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label>Modell</Label>
                <div className="font-medium">{editingPricing.model_name}</div>
                <div className="text-sm text-muted-foreground">{editingPricing.provider_name}</div>
              </div>

              <div className="grid gap-2">
                <Label>Basispreise (€/1k Tokens)</Label>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Input:</span>
                    <div className="font-mono">€{editingPricing.input_price_per_1k_tokens.toFixed(6)}</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Output:</span>
                    <div className="font-mono">€{editingPricing.output_price_per_1k_tokens.toFixed(6)}</div>
                  </div>
                </div>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="markup">Markup Prozentsatz (%)</Label>
                <Input
                  id="markup"
                  type="number"
                  step="0.1"
                  min="0"
                  value={editFormData.markup_percentage}
                  onChange={(e) =>
                    setEditFormData({
                      ...editFormData,
                      markup_percentage: parseFloat(e.target.value) || 0,
                    })
                  }
                />
              </div>

              <div className="grid gap-2">
                <Label>Effektive Preise (€/1k Tokens)</Label>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Input:</span>
                    <div className="font-mono font-semibold text-green-600">
                      €
                      {(
                        editingPricing.input_price_per_1k_tokens *
                        (1 + editFormData.markup_percentage / 100)
                      ).toFixed(6)}
                    </div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Output:</span>
                    <div className="font-mono font-semibold text-green-600">
                      €
                      {(
                        editingPricing.output_price_per_1k_tokens *
                        (1 + editFormData.markup_percentage / 100)
                      ).toFixed(6)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setEditingPricing(null)}
              disabled={loading}
            >
              Abbrechen
            </Button>
            <Button onClick={handleSave} disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Speichern
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
