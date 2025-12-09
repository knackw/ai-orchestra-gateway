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
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { updateUser, User } from '@/lib/actions/admin/users'
import { getTenants, Tenant } from '@/lib/actions/admin/tenants'
import { toast } from 'sonner'
import { Loader2 } from 'lucide-react'

interface EditUserDialogProps {
  user: User
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

export function EditUserDialog({
  user,
  open,
  onOpenChange,
  onSuccess,
}: EditUserDialogProps) {
  const [loading, setLoading] = useState(false)
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [formData, setFormData] = useState({
    role: user.role,
    tenant_id: user.tenant_id || '',
  })

  useEffect(() => {
    if (open) {
      loadTenants()
      setFormData({
        role: user.role,
        tenant_id: user.tenant_id || '',
      })
    }
  }, [open, user])

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
      await updateUser(user.id, {
        role: formData.role,
        tenant_id: formData.tenant_id || null,
      })

      toast.success('Benutzer erfolgreich aktualisiert')
      onOpenChange(false)
      onSuccess?.()
    } catch (error) {
      toast.error('Fehler beim Aktualisieren des Benutzers')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Benutzer bearbeiten</DialogTitle>
          <DialogDescription>
            Bearbeiten Sie die Rolle und Mandantenzuweisung des Benutzers
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label>E-Mail-Adresse</Label>
              <div className="text-sm font-medium">{user.email}</div>
            </div>

            <div className="grid gap-2">
              <Label>Name</Label>
              <div className="text-sm">{user.full_name || '-'}</div>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="role">Rolle *</Label>
              <Select
                value={formData.role}
                onValueChange={(value) =>
                  setFormData({ ...formData, role: value })
                }
                required
              >
                <SelectTrigger id="role">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="user">Benutzer</SelectItem>
                  <SelectItem value="viewer">Betrachter</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="tenant_id">Mandant</Label>
              <Select
                value={formData.tenant_id}
                onValueChange={(value) =>
                  setFormData({ ...formData, tenant_id: value })
                }
              >
                <SelectTrigger id="tenant_id">
                  <SelectValue placeholder="Kein Mandant" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Kein Mandant</SelectItem>
                  {tenants.map((tenant) => (
                    <SelectItem key={tenant.id} value={tenant.id}>
                      {tenant.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
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
              Speichern
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
