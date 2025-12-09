'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Input } from '@/components/ui/input'
import { Loader2, Info } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface ApiSettings {
  defaultProvider: string
  euOnlyMode: boolean
  rateLimitPerMinute: number
  webhookUrl?: string
}

interface ApiSettingsProps {
  initialSettings: ApiSettings
  onUpdate: (settings: ApiSettings) => Promise<void>
}

const providers = [
  { value: 'anthropic', label: 'Anthropic Claude' },
  { value: 'scaleway', label: 'Scaleway AI' },
  { value: 'openai', label: 'OpenAI (Coming Soon)', disabled: true },
]

export function ApiSettings({
  initialSettings,
  onUpdate,
}: ApiSettingsProps) {
  const [defaultProvider, setDefaultProvider] = useState(initialSettings.defaultProvider)
  const [euOnlyMode, setEuOnlyMode] = useState(initialSettings.euOnlyMode)
  const [rateLimitPerMinute, setRateLimitPerMinute] = useState(
    initialSettings.rateLimitPerMinute.toString()
  )
  const [webhookUrl, setWebhookUrl] = useState(initialSettings.webhookUrl || '')
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await onUpdate({
        defaultProvider,
        euOnlyMode,
        rateLimitPerMinute: parseInt(rateLimitPerMinute, 10),
        webhookUrl: webhookUrl || undefined,
      })

      toast({
        title: 'API Settings Updated',
        description: 'Your API settings have been saved successfully.',
      })
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to update API settings.',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Provider Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Provider Settings</CardTitle>
          <CardDescription>
            Configure your default AI provider and regional preferences
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="provider">Default AI Provider</Label>
              <Select value={defaultProvider} onValueChange={setDefaultProvider}>
                <SelectTrigger id="provider">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {providers.map((provider) => (
                    <SelectItem
                      key={provider.value}
                      value={provider.value}
                      disabled={provider.disabled}
                    >
                      {provider.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                The default provider to use when not specified in requests
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="eu-only">EU-Only Mode</Label>
                  <p className="text-xs text-muted-foreground">
                    Process all requests within EU data centers only
                  </p>
                </div>
                <Switch
                  id="eu-only"
                  checked={euOnlyMode}
                  onCheckedChange={setEuOnlyMode}
                />
              </div>
              {euOnlyMode && (
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    EU-Only mode ensures GDPR compliance by processing all data
                    within European Union boundaries. This may affect performance
                    and model availability.
                  </AlertDescription>
                </Alert>
              )}
            </div>

            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save Provider Settings
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Rate Limiting */}
      <Card>
        <CardHeader>
          <CardTitle>Rate Limiting</CardTitle>
          <CardDescription>
            Configure request rate limits for your API keys
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="rate-limit">Requests per Minute</Label>
              <Input
                id="rate-limit"
                type="number"
                min="1"
                max="1000"
                value={rateLimitPerMinute}
                onChange={(e) => setRateLimitPerMinute(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Maximum number of API requests allowed per minute (1-1000)
              </p>
            </div>

            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save Rate Limit
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Webhooks */}
      <Card>
        <CardHeader>
          <CardTitle>Webhooks</CardTitle>
          <CardDescription>
            Configure webhook endpoints for real-time notifications
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="webhook-url">Webhook URL</Label>
              <Input
                id="webhook-url"
                type="url"
                placeholder="https://your-domain.com/webhook"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Receive notifications about API events, billing, and security alerts
              </p>
            </div>

            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                Webhook events include: credit low warnings, invoice generation,
                API key creation/deletion, and security alerts. Your endpoint must
                respond with HTTP 200 within 5 seconds.
              </AlertDescription>
            </Alert>

            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save Webhook Settings
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
