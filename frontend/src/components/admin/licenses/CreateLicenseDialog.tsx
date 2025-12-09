'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { createLicense } from '@/lib/actions/admin/licenses'
import { getTenants, Tenant } from '@/lib/actions/admin/tenants'
import { toast } from 'sonner'
import { Loader2 } from 'lucide-react'

interface CreateLicenseDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

export function CreateLicenseDialog({
  open,
  onOpenChange,
  onSuccess,
}: CreateLicenseDialogProps) {
  const [loading, setLoading] = useState(false)
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [formData, setFormData] = useState({
    tenant_id: '',
    plan: 'starter',
    initial_credits: 10000,
  })

  useEffect(() => {
    if (open) {
      loadTenants()
    }
  }, [open])

  const loadTenants = async () => {
    try {
      const data = await getTenants()
      setTenants(data.filter((t) => t.is_active))
    } catch (error) {
      toast.error('Fehler beim Laden der Mandanten')
      console.error(error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await createLicense({
        tenant_id: formData.tenant_id,
        plan: formData.plan,
        initial_credits: formData.initial_credits,
      })

      toast.success('Lizenz erfolgreich erstellt')
      onOpenChange(false)
      onSuccess?.()
      setFormData({
        tenant_id: '',
        plan: 'starter',
        initial_credits: 10000,
      })
    } catch (error) {
      toast.error('Fehler beim Erstellen der Lizenz')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Neue Lizenz erstellen</DialogTitle>
          <DialogDescription>
            Erstellen Sie eine neue Lizenz für einen Mandanten
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="tenant_id">Mandant *</Label>
              <Select
                value={formData.tenant_id}
                onValueChange={(value) =>
                  setFormData({ ...formData, tenant_id: value })
                }
                required
              >
                <SelectTrigger id="tenant_id">
                  <SelectValue placeholder="Mandant auswählen" />
                </SelectTrigger>
                <SelectContent>
                  {tenants.map((tenant) => (
                    <SelectItem key={tenant.id} value={tenant.id}>
                      {tenant.name} ({tenant.email})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="plan">Plan *</Label>
              <Select
                value={formData.plan}
                onValueChange={(value) =>
                  setFormData({ ...formData, plan: value })
                }
                required
              >
                <SelectTrigger id="plan">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="starter">Starter</SelectItem>
                  <SelectItem value="professional">Professional</SelectItem>
                  <SelectItem value="enterprise">Enterprise</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="initial_credits">Initiale Credits *</Label>
              <Input
                id="initial_credits"
                type="number"
                min="0"
                value={formData.initial_credits}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    initial_credits: parseInt(e.target.value) || 0,
                  })
                }
                required
              />
              <p className="text-xs text-muted-foreground">
                Credits werden dem Mandantenkonto gutgeschrieben
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              Abbrechen
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Lizenz erstellen
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
