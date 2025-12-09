'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { testPrivacyShield, PIIDetectionResult } from '@/lib/actions/admin/privacy'
import { Shield, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react'
import { toast } from 'sonner'

export default function PrivacyTestPage() {
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PIIDetectionResult | null>(null)

  const exampleTexts = {
    email: 'Kontaktieren Sie uns unter max.mustermann@example.com für weitere Informationen.',
    phone: 'Rufen Sie uns an unter +49 123 4567890 oder 0171 1234567.',
    iban: 'Überweisen Sie bitte an IBAN: DE89 3704 0044 0532 0130 00.',
    mixed: 'Herr Max Mustermann (max@example.com) hat von seinem Konto DE89370400440532013000 überwiesen. Tel: +49 30 12345678.',
  }

  const handleTest = async () => {
    if (!inputText.trim()) {
      toast.error('Bitte geben Sie einen Text ein')
      return
    }

    setLoading(true)
    try {
      const data = await testPrivacyShield(inputText)
      setResult(data)
      if (data.has_pii) {
        toast.warning(`${data.detections.length} PII-Erkennungen gefunden`)
      } else {
        toast.success('Keine PII erkannt')
      }
    } catch (error) {
      toast.error('Fehler beim Testen des Privacy Shield')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const loadExample = (key: keyof typeof exampleTexts) => {
    setInputText(exampleTexts[key])
    setResult(null)
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Shield className="h-8 w-8" />
          Privacy Shield Test Console
        </h1>
        <p className="text-muted-foreground mt-2">
          Testen Sie die PII-Erkennung und -Anonymisierung
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Input Section */}
        <Card>
          <CardHeader>
            <CardTitle>Eingabe</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2 flex-wrap">
              <Button
                variant="outline"
                size="sm"
                onClick={() => loadExample('email')}
              >
                Email Beispiel
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => loadExample('phone')}
              >
                Telefon Beispiel
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => loadExample('iban')}
              >
                IBAN Beispiel
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => loadExample('mixed')}
              >
                Gemischt
              </Button>
            </div>

            <Textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Geben Sie hier einen Text ein, um ihn auf PII zu testen..."
              rows={12}
              className="font-mono text-sm"
            />

            <Button
              onClick={handleTest}
              disabled={loading || !inputText.trim()}
              className="w-full"
            >
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Privacy Shield testen
            </Button>
          </CardContent>
        </Card>

        {/* Results Section */}
        <Card>
          <CardHeader>
            <CardTitle>Ergebnisse</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {result ? (
              <>
                {/* Status Alert */}
                <Alert variant={result.has_pii ? 'destructive' : 'default'}>
                  {result.has_pii ? (
                    <AlertTriangle className="h-4 w-4" />
                  ) : (
                    <CheckCircle className="h-4 w-4" />
                  )}
                  <AlertDescription>
                    {result.has_pii
                      ? `${result.detections.length} PII-Erkennung(en) gefunden`
                      : 'Keine personenbezogenen Daten erkannt'}
                  </AlertDescription>
                </Alert>

                {/* Detections */}
                {result.detections.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-semibold text-sm">Erkannte PII:</h4>
                    <div className="space-y-2">
                      {result.detections.map((detection, idx) => (
                        <Card key={idx} className="bg-muted">
                          <CardContent className="pt-4">
                            <div className="flex items-center justify-between mb-2">
                              <Badge variant="destructive">
                                {detection.type}
                              </Badge>
                              <span className="text-xs text-muted-foreground">
                                Position: {detection.position}
                              </span>
                            </div>
                            <code className="text-sm bg-background p-2 rounded block">
                              {detection.value}
                            </code>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {/* Sanitized Output */}
                <div className="space-y-2">
                  <h4 className="font-semibold text-sm">Anonymisierter Text:</h4>
                  <Card className="bg-green-50 dark:bg-green-950">
                    <CardContent className="pt-4">
                      <pre className="text-sm whitespace-pre-wrap font-mono">
                        {result.sanitized_text}
                      </pre>
                    </CardContent>
                  </Card>
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-96 text-muted-foreground">
                <div className="text-center">
                  <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Geben Sie Text ein und klicken Sie auf "Testen"</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle>Unterstützte PII-Typen</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <Badge>Email</Badge>
              <p className="text-xs text-muted-foreground mt-1">
                E-Mail-Adressen
              </p>
            </div>
            <div>
              <Badge>Telefon</Badge>
              <p className="text-xs text-muted-foreground mt-1">
                Telefonnummern (DE)
              </p>
            </div>
            <div>
              <Badge>IBAN</Badge>
              <p className="text-xs text-muted-foreground mt-1">
                Bankkontonummern
              </p>
            </div>
            <div>
              <Badge>Namen</Badge>
              <p className="text-xs text-muted-foreground mt-1">
                Personennamen (optional)
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
