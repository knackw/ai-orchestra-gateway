'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import {
  getProviders,
  LLMProvider,
  updateProvider,
  deleteProvider,
} from '@/lib/actions/admin/llm-config'
import { Plus, Settings, Trash2, Globe } from 'lucide-react'
import { toast } from 'sonner'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'

export default function LLMConfigPage() {
  const [providers, setProviders] = useState<LLMProvider[]>([])
  const [loading, setLoading] = useState(true)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [providerToDelete, setProviderToDelete] = useState<string | null>(null)

  useEffect(() => {
    loadProviders()
  }, [])

  const loadProviders = async () => {
    try {
      const data = await getProviders()
      setProviders(data)
    } catch (error) {
      toast.error('Fehler beim Laden der Provider')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleActive = async (id: string, isActive: boolean) => {
    try {
      await updateProvider(id, { is_active: !isActive })
      toast.success(isActive ? 'Provider deaktiviert' : 'Provider aktiviert')
      loadProviders()
    } catch (error) {
      toast.error('Fehler beim Aktualisieren des Providers')
      console.error(error)
    }
  }

  const handleToggleEuOnly = async (id: string, euOnly: boolean) => {
    try {
      await updateProvider(id, { eu_only: !euOnly })
      toast.success('EU-Only Einstellung aktualisiert')
      loadProviders()
    } catch (error) {
      toast.error('Fehler beim Aktualisieren')
      console.error(error)
    }
  }

  const handleDelete = async () => {
    if (!providerToDelete) return

    try {
      await deleteProvider(providerToDelete)
      toast.success('Provider gelöscht')
      setDeleteDialogOpen(false)
      loadProviders()
    } catch (error) {
      toast.error('Fehler beim Löschen')
      console.error(error)
    }
  }

  const getProviderIcon = (type: string) => {
    const icons: Record<string, string> = {
      anthropic: '🤖',
      scaleway: '☁️',
      openai: '🔮',
      custom: '⚙️',
    }
    return icons[type] || '🔧'
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

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Settings className="h-8 w-8" />
            LLM Provider Konfiguration
          </h1>
          <p className="text-muted-foreground mt-2">
            Verwalten Sie AI Provider und Modelle
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Provider hinzufügen
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {providers.map((provider) => (
          <Card key={provider.id} className={!provider.is_active ? 'opacity-60' : ''}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <span className="text-2xl">{getProviderIcon(provider.type)}</span>
                    {provider.name}
                  </CardTitle>
                  <CardDescription className="mt-1">
                    <Badge variant="outline" className="mt-2">
                      {provider.type}
                    </Badge>
                  </CardDescription>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setProviderToDelete(provider.id)
                    setDeleteDialogOpen(true)
                  }}
                >
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor={`active-${provider.id}`}>Aktiv</Label>
                  <Switch
                    id={`active-${provider.id}`}
                    checked={provider.is_active}
                    onCheckedChange={() => handleToggleActive(provider.id, provider.is_active)}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <Label htmlFor={`eu-${provider.id}`} className="flex items-center gap-2">
                    <Globe className="h-4 w-4" />
                    Nur EU
                  </Label>
                  <Switch
                    id={`eu-${provider.id}`}
                    checked={provider.eu_only}
                    onCheckedChange={() => handleToggleEuOnly(provider.id, provider.eu_only)}
                  />
                </div>
              </div>

              {provider.base_url && (
                <div className="text-xs text-muted-foreground">
                  <span className="font-semibold">Base URL:</span>
                  <br />
                  <code className="bg-muted px-1 py-0.5 rounded">
                    {provider.base_url}
                  </code>
                </div>
              )}

              <div>
                <span className="text-sm font-semibold">Modelle:</span>
                <div className="mt-2 space-y-1">
                  {provider.models && provider.models.length > 0 ? (
                    provider.models.slice(0, 3).map((model) => (
                      <div
                        key={model.id}
                        className="text-xs bg-muted px-2 py-1 rounded flex items-center justify-between"
                      >
                        <span>{model.display_name}</span>
                        {model.is_active && (
                          <Badge variant="outline" className="text-xs">
                            Aktiv
                          </Badge>
                        )}
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-muted-foreground">Keine Modelle</p>
                  )}
                  {provider.models && provider.models.length > 3 && (
                    <p className="text-xs text-muted-foreground">
                      +{provider.models.length - 3} weitere
                    </p>
                  )}
                </div>
              </div>

              <div className="pt-2">
                <Button variant="outline" size="sm" className="w-full">
                  Konfigurieren
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {providers.length === 0 && (
        <Card>
          <CardContent className="py-12">
            <div className="text-center text-muted-foreground">
              <Settings className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Keine Provider konfiguriert</p>
              <Button className="mt-4">
                <Plus className="mr-2 h-4 w-4" />
                Ersten Provider hinzufügen
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Provider löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              Diese Aktion kann nicht rückgängig gemacht werden. Der Provider und alle zugehörigen
              Konfigurationen werden dauerhaft gelöscht.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground">
              Löschen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
