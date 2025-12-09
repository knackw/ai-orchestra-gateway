'use client'

import { useState } from 'react'
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
import { Textarea } from '@/components/ui/textarea'
import { addCredits, License } from '@/lib/actions/admin/licenses'
import { toast } from 'sonner'
import { Loader2 } from 'lucide-react'

interface AddCreditsDialogProps {
  license: License
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

export function AddCreditsDialog({
  license,
  open,
  onOpenChange,
  onSuccess,
}: AddCreditsDialogProps) {
  const [loading, setLoading] = useState(false)
  const [amount, setAmount] = useState(1000)
  const [note, setNote] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await addCredits({
        license_id: license.id,
        amount,
        note: note || undefined,
      })

      toast.success(`${amount} Credits erfolgreich hinzugefügt`)
      onOpenChange(false)
      onSuccess?.()
      setAmount(1000)
      setNote('')
    } catch (error) {
      toast.error('Fehler beim Hinzufügen der Credits')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Credits hinzufügen</DialogTitle>
          <DialogDescription>
            Credits zur Lizenz hinzufügen: {license.key.substring(0, 24)}...
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label>Mandant</Label>
              <div className="text-sm">
                <div className="font-medium">{license.tenant?.name}</div>
                <div className="text-muted-foreground">{license.tenant?.email}</div>
              </div>
            </div>

            <div className="grid gap-2">
              <Label>Aktuelle Credits</Label>
              <div className="text-2xl font-bold">
                {license.credits_remaining.toLocaleString('de-DE')}
              </div>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="amount">Hinzuzufügende Credits *</Label>
              <Input
                id="amount"
                type="number"
                min="1"
                value={amount}
                onChange={(e) => setAmount(parseInt(e.target.value) || 0)}
                required
              />
              <div className="text-sm text-muted-foreground">
                Neue Summe: {(license.credits_remaining + amount).toLocaleString('de-DE')} Credits
              </div>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="note">Notiz (optional)</Label>
              <Textarea
                id="note"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Grund für die Credit-Zuteilung..."
                rows={3}
              />
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
              Credits hinzufügen
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
