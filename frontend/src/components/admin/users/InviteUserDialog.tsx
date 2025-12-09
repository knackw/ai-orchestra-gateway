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
import { inviteUser } from '@/lib/actions/admin/users'
import { getTenants, Tenant } from '@/lib/actions/admin/tenants'
import { toast } from 'sonner'
import { Loader2 } from 'lucide-react'

interface InviteUserDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

export function InviteUserDialog({
  open,
  onOpenChange,
  onSuccess,
}: InviteUserDialogProps) {
  const [loading, setLoading] = useState(false)
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    role: 'user',
    tenant_id: '',
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
      await inviteUser({
        email: formData.email,
        full_name: formData.full_name,
        role: formData.role,
        tenant_id: formData.tenant_id || undefined,
      })

      toast.success('Benutzer erfolgreich eingeladen')
      onOpenChange(false)
      onSuccess?.()
      setFormData({
        email: '',
        full_name: '',
        role: 'user',
        tenant_id: '',
      })
    } catch (error) {
      toast.error('Fehler beim Einladen des Benutzers')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Benutzer einladen</DialogTitle>
          <DialogDescription>
            Laden Sie einen neuen Benutzer ein. Eine Einladungs-E-Mail wird gesendet.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="email">E-Mail-Adresse *</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                required
                placeholder="benutzer@example.com"
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="full_name">Vollständiger Name *</Label>
              <Input
                id="full_name"
                type="text"
                value={formData.full_name}
                onChange={(e) =>
                  setFormData({ ...formData, full_name: e.target.value })
                }
                required
                placeholder="Max Mustermann"
              />
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
              <p className="text-xs text-muted-foreground">
                Admin: Voller Zugriff | Benutzer: API-Zugriff | Betrachter: Nur Leserechte
              </p>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="tenant_id">Mandant (optional)</Label>
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
              Benutzer einladen
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
