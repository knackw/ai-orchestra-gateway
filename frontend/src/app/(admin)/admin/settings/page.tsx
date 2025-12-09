'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Switch } from '@/components/ui/switch'
import { getSettings, updateSettings, AppSettings } from '@/lib/actions/admin/settings'
import { toast } from 'sonner'

export default function AdminSettingsPage() {
  const [settings, setSettings] = useState<AppSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const data = await getSettings()
      setSettings(data)
    } catch {
      toast.error('Fehler beim Laden der Einstellungen')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (updates: Partial<AppSettings>) => {
    setSaving(true)
    try {
      const updated = await updateSettings(updates)
      setSettings(updated)
      toast.success('Einstellungen gespeichert')
    } catch {
      toast.error('Fehler beim Speichern')
    } finally {
      setSaving(false)
    }
  }

  if (loading || !settings) {
    return <div className="container mx-auto p-6">Lädt...</div>
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Systemeinstellungen</h1>
        <p className="text-muted-foreground">Konfigurieren Sie systemweite Einstellungen</p>
      </div>

      <Tabs defaultValue="general" className="space-y-6">
        <TabsList>
          <TabsTrigger value="general">Allgemein</TabsTrigger>
          <TabsTrigger value="billing">Abrechnung</TabsTrigger>
          <TabsTrigger value="providers">AI-Anbieter</TabsTrigger>
          <TabsTrigger value="security">Sicherheit</TabsTrigger>
          <TabsTrigger value="email">E-Mail</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Allgemeine Einstellungen</CardTitle>
              <CardDescription>Grundlegende Anwendungskonfiguration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="app_name">Anwendungsname</Label>
                <Input
                  id="app_name"
                  value={settings.app_name}
                  onChange={(e) => setSettings({ ...settings, app_name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="support_email">Support-E-Mail</Label>
                <Input
                  id="support_email"
                  type="email"
                  value={settings.support_email}
                  onChange={(e) => setSettings({ ...settings, support_email: e.target.value })}
                />
              </div>
              <Button onClick={() => handleSave({ app_name: settings.app_name, support_email: settings.support_email })} disabled={saving}>
                Änderungen speichern
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="billing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Abrechnungseinstellungen</CardTitle>
              <CardDescription>Konfigurieren Sie Standardpläne und Preise</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="default_plan">Standardplan</Label>
                <Input
                  id="default_plan"
                  value={settings.default_plan}
                  onChange={(e) => setSettings({ ...settings, default_plan: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="credit_pricing">Credit-Preis (EUR)</Label>
                <Input
                  id="credit_pricing"
                  type="number"
                  step="0.001"
                  value={settings.credit_pricing}
                  onChange={(e) => setSettings({ ...settings, credit_pricing: parseFloat(e.target.value) })}
                />
              </div>
              <Button onClick={() => handleSave({ default_plan: settings.default_plan, credit_pricing: settings.credit_pricing })} disabled={saving}>
                Änderungen speichern
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="providers" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>AI-Anbieter</CardTitle>
              <CardDescription>Aktivieren/Deaktivieren Sie AI-Anbieter</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="anthropic">Anthropic</Label>
                  <p className="text-sm text-muted-foreground">Claude-Modelle</p>
                </div>
                <Switch
                  id="anthropic"
                  checked={settings.anthropic_enabled}
                  onCheckedChange={(checked) => handleSave({ anthropic_enabled: checked })}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="scaleway">Scaleway</Label>
                  <p className="text-sm text-muted-foreground">Scaleway AI-Modelle</p>
                </div>
                <Switch
                  id="scaleway"
                  checked={settings.scaleway_enabled}
                  onCheckedChange={(checked) => handleSave({ scaleway_enabled: checked })}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="openai">OpenAI</Label>
                  <p className="text-sm text-muted-foreground">GPT-Modelle</p>
                </div>
                <Switch
                  id="openai"
                  checked={settings.openai_enabled}
                  onCheckedChange={(checked) => handleSave({ openai_enabled: checked })}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Sicherheitseinstellungen</CardTitle>
              <CardDescription>Rate-Limits und IP-Whitelist</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="rate_limit_minute">Rate-Limit pro Minute</Label>
                <Input
                  id="rate_limit_minute"
                  type="number"
                  value={settings.rate_limit_per_minute}
                  onChange={(e) => setSettings({ ...settings, rate_limit_per_minute: parseInt(e.target.value) })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="rate_limit_hour">Rate-Limit pro Stunde</Label>
                <Input
                  id="rate_limit_hour"
                  type="number"
                  value={settings.rate_limit_per_hour}
                  onChange={(e) => setSettings({ ...settings, rate_limit_per_hour: parseInt(e.target.value) })}
                />
              </div>
              <Button onClick={() => handleSave({ rate_limit_per_minute: settings.rate_limit_per_minute, rate_limit_per_hour: settings.rate_limit_per_hour })} disabled={saving}>
                Änderungen speichern
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="email" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>E-Mail-Einstellungen</CardTitle>
              <CardDescription>SMTP-Konfiguration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="smtp_host">SMTP-Host</Label>
                <Input
                  id="smtp_host"
                  value={settings.smtp_host || ''}
                  onChange={(e) => setSettings({ ...settings, smtp_host: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="smtp_port">SMTP-Port</Label>
                <Input
                  id="smtp_port"
                  type="number"
                  value={settings.smtp_port || 587}
                  onChange={(e) => setSettings({ ...settings, smtp_port: parseInt(e.target.value) })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="smtp_from">Von-E-Mail</Label>
                <Input
                  id="smtp_from"
                  type="email"
                  value={settings.smtp_from_email || ''}
                  onChange={(e) => setSettings({ ...settings, smtp_from_email: e.target.value })}
                />
              </div>
              <Button onClick={() => handleSave({ smtp_host: settings.smtp_host, smtp_port: settings.smtp_port, smtp_from_email: settings.smtp_from_email })} disabled={saving}>
                Änderungen speichern
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
