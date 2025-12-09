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
import { Copy, Check, AlertTriangle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface CreateApiKeyDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

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
        title: 'Error',
        description: 'Please enter a name for the API key',
        variant: 'destructive',
      })
      return
    }

    setLoading(true)
    try {
      // TODO: Replace with actual API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Mock API key - In production, this comes from the API
      const mockKey = `alo_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`

      setCreatedKey(mockKey)
      toast({
        title: 'Success',
        description: 'API key created successfully',
      })

      if (onSuccess) {
        onSuccess()
      }
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to create API key',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = async () => {
    if (createdKey) {
      await navigator.clipboard.writeText(createdKey)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
      toast({
        title: 'Copied',
        description: 'API key copied to clipboard',
      })
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
            {createdKey ? 'API Key Created' : 'Create New API Key'}
          </DialogTitle>
          <DialogDescription>
            {createdKey
              ? 'Save this key somewhere safe. You won&apos;t be able to see it again.'
              : 'Create a new API key to access the AI Orchestra API.'}
          </DialogDescription>
        </DialogHeader>

        {!createdKey ? (
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Key Name</Label>
              <Input
                id="name"
                placeholder="e.g., Production Key"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={loading}
              />
              <p className="text-sm text-muted-foreground">
                A descriptive name to help you identify this key
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4 py-4">
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Make sure to copy your API key now. You won&apos;t be able to see it
                again!
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <Label>Your API Key</Label>
              <div className="flex gap-2">
                <Input
                  value={createdKey}
                  readOnly
                  className="font-mono"
                />
                <Button
                  size="icon"
                  variant="outline"
                  onClick={handleCopy}
                >
                  {copied ? (
                    <Check className="h-4 w-4" />
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
                Cancel
              </Button>
              <Button onClick={handleCreate} disabled={loading}>
                {loading ? 'Creating...' : 'Create Key'}
              </Button>
            </>
          ) : (
            <Button onClick={handleClose} className="w-full">
              Done
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
