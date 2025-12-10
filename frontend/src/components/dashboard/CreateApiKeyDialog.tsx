'use client'

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Copy, Check, AlertTriangle, Loader2 } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { createApiKey } from '@/lib/actions/api-keys'

interface CreateApiKeyDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

/**
 * SEC-005: Secure API Key Creation Dialog
 *
 * Uses server actions for secure API key creation.
 * The API key is only shown once - users must copy it immediately.
 */
export function CreateApiKeyDialog({
  open,
  onOpenChange,
  onSuccess,
}: CreateApiKeyDialogProps) {
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [createdKey, setCreatedKey] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const { toast } = useToast()

  const handleCreate = async () => {
    if (!name.trim()) {
      toast({
        title: 'Fehler',
        description: 'Bitte geben Sie einen Namen für den API-Schlüssel ein',
        variant: 'destructive',
      })
      return
    }

    setLoading(true)
    try {
      // Use the secure server action
      const result = await createApiKey(name.trim())

      if (result.success && result.data) {
        setCreatedKey(result.data.key)
        toast({
          title: 'Erfolg',
          description: 'API-Schlüssel wurde erfolgreich erstellt',
        })

        if (onSuccess) {
          onSuccess()
        }
      } else {
        toast({
          title: 'Fehler',
          description: result.error || 'API-Schlüssel konnte nicht erstellt werden',
          variant: 'destructive',
        })
      }
    } catch {
      toast({
        title: 'Fehler',
        description: 'API-Schlüssel konnte nicht erstellt werden',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = async () => {
    if (createdKey) {
      try {
        await navigator.clipboard.writeText(createdKey)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
        toast({
          title: 'Kopiert',
          description: 'API-Schlüssel wurde in die Zwischenablage kopiert',
        })
      } catch {
        toast({
          title: 'Fehler',
          description: 'Kopieren fehlgeschlagen. Bitte manuell kopieren.',
          variant: 'destructive',
        })
      }
    }
  }

  const handleClose = () => {
    setName('')
    setCreatedKey(null)
    setCopied(false)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {createdKey ? 'API-Schlüssel erstellt' : 'Neuen API-Schlüssel erstellen'}
          </DialogTitle>
          <DialogDescription>
            {createdKey
              ? 'Speichern Sie diesen Schlüssel sicher. Sie werden ihn nicht erneut sehen können.'
              : 'Erstellen Sie einen neuen API-Schlüssel für den Zugriff auf die AI Orchestra API.'}
          </DialogDescription>
        </DialogHeader>

        {!createdKey ? (
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Schlüsselname</Label>
              <Input
                id="name"
                placeholder="z.B. Produktions-Schlüssel"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={loading}
                maxLength={100}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !loading && name.trim()) {
                    e.preventDefault()
                    handleCreate()
                  }
                }}
              />
              <p className="text-sm text-muted-foreground">
                Ein beschreibender Name, um diesen Schlüssel zu identifizieren
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4 py-4">
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Kopieren Sie Ihren API-Schlüssel jetzt. Sie werden ihn nicht erneut
                sehen können!
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <Label>Ihr API-Schlüssel</Label>
              <div className="flex gap-2">
                <Input
                  value={createdKey}
                  readOnly
                  className="font-mono text-sm"
                />
                <Button
                  size="icon"
                  variant="outline"
                  onClick={handleCopy}
                  title="In Zwischenablage kopieren"
                >
                  {copied ? (
                    <Check className="h-4 w-4 text-green-600" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </div>
        )}

        <DialogFooter>
          {!createdKey ? (
            <>
              <Button variant="outline" onClick={handleClose} disabled={loading}>
                Abbrechen
              </Button>
              <Button onClick={handleCreate} disabled={loading || !name.trim()}>
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {loading ? 'Erstelle...' : 'Schlüssel erstellen'}
              </Button>
            </>
          ) : (
            <Button onClick={handleClose} className="w-full">
              Fertig
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
