'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'
import { generatePlayground, PlaygroundResponse } from '@/lib/actions/admin/playground'
import { getProviders, LLMProvider } from '@/lib/actions/admin/llm-config'
import { Loader2, Play, Sparkles, Clock, Coins } from 'lucide-react'
import { toast } from 'sonner'

export default function PlaygroundPage() {
  const [providers, setProviders] = useState<LLMProvider[]>([])
  const [selectedProvider, setSelectedProvider] = useState('')
  const [selectedModel, setSelectedModel] = useState('')
  const [prompt, setPrompt] = useState('')
  const [systemPrompt, setSystemPrompt] = useState('')
  const [temperature, setTemperature] = useState([0.7])
  const [maxTokens, setMaxTokens] = useState([1000])
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState<PlaygroundResponse | null>(null)

  useEffect(() => {
    loadProviders()
  }, [])

  const loadProviders = async () => {
    try {
      const data = await getProviders()
      setProviders(data.filter((p) => p.is_active))
    } catch (error) {
      toast.error('Fehler beim Laden der Provider')
      console.error(error)
    }
  }

  const selectedProviderData = providers.find((p) => p.id === selectedProvider)
  const availableModels = selectedProviderData?.models?.filter((m) => m.is_active) || []

  const handleGenerate = async () => {
    if (!selectedProvider || !selectedModel || !prompt.trim()) {
      toast.error('Bitte füllen Sie alle Pflichtfelder aus')
      return
    }

    setLoading(true)
    setResponse(null)

    try {
      const result = await generatePlayground({
        provider: selectedProvider,
        model: selectedModel,
        prompt: prompt,
        system_prompt: systemPrompt || undefined,
        temperature: temperature[0],
        max_tokens: maxTokens[0],
      })
      setResponse(result)
      toast.success('Antwort generiert')
    } catch (error) {
      toast.error('Fehler beim Generieren')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Sparkles className="h-8 w-8" />
          AI Playground
        </h1>
        <p className="text-muted-foreground mt-2">
          Testen Sie verschiedene AI-Modelle und Parameter
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Configuration Panel */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Konfiguration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Provider</Label>
                <Select
                  value={selectedProvider}
                  onValueChange={(value) => {
                    setSelectedProvider(value)
                    setSelectedModel('')
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Provider auswählen" />
                  </SelectTrigger>
                  <SelectContent>
                    {providers.map((provider) => (
                      <SelectItem key={provider.id} value={provider.id}>
                        {provider.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Modell</Label>
                <Select
                  value={selectedModel}
                  onValueChange={setSelectedModel}
                  disabled={!selectedProvider}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Modell auswählen" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableModels.map((model) => (
                      <SelectItem key={model.id} value={model.name}>
                        {model.display_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label>Temperature</Label>
                  <span className="text-sm text-muted-foreground">{temperature[0]}</span>
                </div>
                <Slider
                  value={temperature}
                  onValueChange={setTemperature}
                  min={0}
                  max={2}
                  step={0.1}
                />
                <p className="text-xs text-muted-foreground">
                  Niedrig: konservativ, Hoch: kreativ
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <Label>Max Tokens</Label>
                  <span className="text-sm text-muted-foreground">{maxTokens[0]}</span>
                </div>
                <Slider
                  value={maxTokens}
                  onValueChange={setMaxTokens}
                  min={100}
                  max={4000}
                  step={100}
                />
              </div>

              <div className="space-y-2">
                <Label>System Prompt (optional)</Label>
                <Textarea
                  value={systemPrompt}
                  onChange={(e) => setSystemPrompt(e.target.value)}
                  placeholder="z.B. Du bist ein hilfreicher Assistent..."
                  rows={3}
                />
              </div>

              <Button
                onClick={handleGenerate}
                disabled={loading || !selectedProvider || !selectedModel || !prompt.trim()}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generiert...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Generieren
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Input/Output Panel */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Prompt</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Geben Sie hier Ihren Prompt ein..."
                rows={8}
              />
            </CardContent>
          </Card>

          {response && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Antwort</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="bg-muted p-4 rounded-lg">
                    <pre className="whitespace-pre-wrap font-mono text-sm">
                      {response.response}
                    </pre>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Metriken</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                        <Coins className="h-4 w-4" />
                        Input Tokens
                      </div>
                      <div className="text-2xl font-bold">
                        {response.tokens_used.input.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                        <Coins className="h-4 w-4" />
                        Output Tokens
                      </div>
                      <div className="text-2xl font-bold">
                        {response.tokens_used.output.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                        <Clock className="h-4 w-4" />
                        Duration
                      </div>
                      <div className="text-2xl font-bold">
                        {(response.duration_ms / 1000).toFixed(2)}s
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                        <Coins className="h-4 w-4" />
                        Cost
                      </div>
                      <div className="text-2xl font-bold">
                        €{response.cost.total_cost.toFixed(4)}
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge>{response.provider}</Badge>
                      <Badge variant="outline">{response.model}</Badge>
                    </div>
                    <div className="text-xs text-muted-foreground space-y-1">
                      <div>Input Cost: €{response.cost.input_cost.toFixed(6)}</div>
                      <div>Output Cost: €{response.cost.output_cost.toFixed(6)}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
