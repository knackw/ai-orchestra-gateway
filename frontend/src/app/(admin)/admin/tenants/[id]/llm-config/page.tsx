'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Switch } from '@/components/ui/switch'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { ArrowLeft, Save, RotateCcw, Shield } from 'lucide-react'
import { getTenant, Tenant } from '@/lib/actions/admin/tenants'
import { getLlmModels, LlmModel, updateTenantLlmConfig } from '@/lib/actions/admin/llm-config'
import { toast } from 'sonner'
import Link from 'next/link'

interface TenantModelConfig {
  model_id: string
  enabled: boolean
  rate_limit?: number
  max_tokens?: number
  custom_pricing?: number
}

export default function TenantLlmConfigPage() {
  const params = useParams()
  const router = useRouter()
  const tenantId = params.id as string

  const [tenant, setTenant] = useState<Tenant | null>(null)
  const [models, setModels] = useState<LlmModel[]>([])
  const [modelConfigs, setModelConfigs] = useState<Record<string, TenantModelConfig>>({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadData()
  }, [tenantId])

  const loadData = async () => {
    try {
      const [tenantData, modelsData] = await Promise.all([
        getTenant(tenantId),
        getLlmModels(),
      ])
      setTenant(tenantData)
      setModels(modelsData)

      const configs: Record<string, TenantModelConfig> = {}
      modelsData.forEach((model) => {
        configs[model.id] = {
          model_id: model.id,
          enabled: model.enabled,
          rate_limit: model.rate_limit,
          max_tokens: model.max_tokens,
        }
      })
      setModelConfigs(configs)
    } catch (error) {
      toast.error('Fehler beim Laden der Daten')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleModel = (modelId: string) => {
    setModelConfigs((prev) => ({
      ...prev,
      [modelId]: {
        ...prev[modelId],
        enabled: !prev[modelId].enabled,
      },
    }))
  }

  const handleRateLimitChange = (modelId: string, value: string) => {
    const numValue = parseInt(value) || undefined
    setModelConfigs((prev) => ({
      ...prev,
      [modelId]: {
        ...prev[modelId],
        rate_limit: numValue,
      },
    }))
  }

  const handleMaxTokensChange = (modelId: string, value: string) => {
    const numValue = parseInt(value) || undefined
    setModelConfigs((prev) => ({
      ...prev,
      [modelId]: {
        ...prev[modelId],
        max_tokens: numValue,
      },
    }))
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await updateTenantLlmConfig(tenantId, Object.values(modelConfigs))
      toast.success('LLM-Konfiguration gespeichert')
      router.push('/admin/tenants')
    } catch (error) {
      toast.error('Fehler beim Speichern der Konfiguration')
      console.error(error)
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    loadData()
    toast.info('Änderungen zurückgesetzt')
  }

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-96">
          <p className="text-muted-foreground">Lädt...</p>
        </div>
      </div>
    )
  }

  if (!tenant) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-lg font-medium mb-2">Mandant nicht gefunden</p>
            <Link href="/admin/tenants">
              <Button variant="outline">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Zurück zu Mandanten
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  const enabledCount = Object.values(modelConfigs).filter((c) => c.enabled).length

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/admin/tenants">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">LLM-Konfiguration</h1>
          <p className="text-muted-foreground">
            Modelle für {tenant.name} konfigurieren
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleReset} disabled={saving}>
            <RotateCcw className="mr-2 h-4 w-4" />
            Zurücksetzen
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            <Save className="mr-2 h-4 w-4" />
            {saving ? 'Speichert...' : 'Speichern'}
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Mandanten-Information</CardTitle>
              <CardDescription>Grundlegende Informationen zum Mandanten</CardDescription>
            </div>
            <Badge variant={tenant.is_active ? 'default' : 'secondary'}>
              {tenant.is_active ? 'Aktiv' : 'Inaktiv'}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label className="text-muted-foreground">Name</Label>
              <div className="font-medium">{tenant.name}</div>
            </div>
            <div>
              <Label className="text-muted-foreground">Email</Label>
              <div className="font-medium">{tenant.email}</div>
            </div>
            <div>
              <Label className="text-muted-foreground">Credits</Label>
              <div className="font-medium">{tenant.credits?.toLocaleString() || 0}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Modell-Konfiguration</CardTitle>
              <CardDescription>
                Aktivieren oder deaktivieren Sie spezifische Modelle für diesen Mandanten
              </CardDescription>
            </div>
            <Badge variant="secondary">
              {enabledCount} von {models.length} aktiviert
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {models.map((model, index) => {
            const config = modelConfigs[model.id]
            if (!config) return null

            return (
              <div key={model.id}>
                {index > 0 && <Separator className="my-6" />}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1 flex-1">
                      <div className="flex items-center gap-2">
                        <Label htmlFor={`model-${model.id}`} className="text-base font-medium">
                          {model.name}
                        </Label>
                        {model.provider === 'anthropic' && (
                          <Badge variant="outline">Anthropic</Badge>
                        )}
                        {model.provider === 'scaleway' && (
                          <Badge variant="outline">Scaleway</Badge>
                        )}
                        {model.eu_compliant && (
                          <Badge variant="outline" className="text-green-600 border-green-600">
                            <Shield className="mr-1 h-3 w-3" />
                            EU
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {model.description || 'Kein Beschreibung verfügbar'}
                      </p>
                    </div>
                    <Switch
                      id={`model-${model.id}`}
                      checked={config.enabled}
                      onCheckedChange={() => handleToggleModel(model.id)}
                    />
                  </div>

                  {config.enabled && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-6">
                      <div className="space-y-2">
                        <Label htmlFor={`rate-${model.id}`}>
                          Rate Limit (Anfragen/Min)
                        </Label>
                        <Input
                          id={`rate-${model.id}`}
                          type="number"
                          value={config.rate_limit || ''}
                          onChange={(e) => handleRateLimitChange(model.id, e.target.value)}
                          placeholder={`Standard: ${model.rate_limit || 'Unbegrenzt'}`}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`tokens-${model.id}`}>
                          Max. Tokens
                        </Label>
                        <Input
                          id={`tokens-${model.id}`}
                          type="number"
                          value={config.max_tokens || ''}
                          onChange={(e) => handleMaxTokensChange(model.id, e.target.value)}
                          placeholder={`Standard: ${model.max_tokens || 'Unbegrenzt'}`}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )
          })}

          {models.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">Keine Modelle verfügbar</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
