'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import { Loader2, ShieldCheck, Eye, EyeOff } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { updatePassword } from '@/lib/actions/profile'

interface SecuritySettingsProps {
  twoFactorEnabled: boolean
  onUpdate: (data: { twoFactorEnabled: boolean }) => Promise<void>
}

/**
 * SEC-012: Password validation matching backend policy
 */
function validatePassword(password: string): string[] {
  const errors: string[] = []

  if (password.length < 12) {
    errors.push('Mindestens 12 Zeichen erforderlich')
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('Mindestens ein Großbuchstabe erforderlich')
  }
  if (!/[a-z]/.test(password)) {
    errors.push('Mindestens ein Kleinbuchstabe erforderlich')
  }
  if (!/[0-9]/.test(password)) {
    errors.push('Mindestens eine Ziffer erforderlich')
  }
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Mindestens ein Sonderzeichen erforderlich')
  }

  return errors
}

export function SecuritySettings({
  twoFactorEnabled: initialTwoFactor,
  onUpdate,
}: SecuritySettingsProps) {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(initialTwoFactor)
  const [loading, setLoading] = useState(false)
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const { toast } = useToast()

  // Real-time password validation
  const passwordErrors = newPassword ? validatePassword(newPassword) : []
  const passwordsMatch = newPassword === confirmPassword

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()

    if (newPassword !== confirmPassword) {
      toast({
        title: 'Fehler',
        description: 'Die Passwörter stimmen nicht überein.',
        variant: 'destructive',
      })
      return
    }

    // Validate password strength (SEC-012)
    const errors = validatePassword(newPassword)
    if (errors.length > 0) {
      toast({
        title: 'Passwort zu schwach',
        description: errors[0],
        variant: 'destructive',
      })
      return
    }

    setLoading(true)
    try {
      // Use the secure server action
      const result = await updatePassword(currentPassword, newPassword)

      if (result.success) {
        toast({
          title: 'Passwort geändert',
          description: 'Ihr Passwort wurde erfolgreich aktualisiert.',
        })

        setCurrentPassword('')
        setNewPassword('')
        setConfirmPassword('')
      } else {
        toast({
          title: 'Fehler',
          description: result.error || 'Passwortänderung fehlgeschlagen.',
          variant: 'destructive',
        })
      }
    } catch {
      toast({
        title: 'Fehler',
        description: 'Passwortänderung fehlgeschlagen.',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const handle2FAToggle = async (enabled: boolean) => {
    setTwoFactorEnabled(enabled)
    try {
      await onUpdate({ twoFactorEnabled: enabled })
      toast({
        title: enabled ? '2FA aktiviert' : '2FA deaktiviert',
        description: enabled
          ? 'Zwei-Faktor-Authentifizierung wurde aktiviert.'
          : 'Zwei-Faktor-Authentifizierung wurde deaktiviert.',
      })
    } catch {
      setTwoFactorEnabled(!enabled)
      toast({
        title: 'Fehler',
        description: '2FA-Einstellungen konnten nicht aktualisiert werden.',
        variant: 'destructive',
      })
    }
  }

  return (
    <div className="space-y-6">
      {/* Change Password */}
      <Card>
        <CardHeader>
          <CardTitle>Passwort ändern</CardTitle>
          <CardDescription>
            Aktualisieren Sie Ihr Passwort, um Ihr Konto sicher zu halten
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="current-password">Aktuelles Passwort</Label>
              <div className="relative">
                <Input
                  id="current-password"
                  type={showCurrentPassword ? 'text' : 'password'}
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  disabled={loading}
                  required
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  disabled={loading}
                >
                  {showCurrentPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="new-password">Neues Passwort</Label>
              <div className="relative">
                <Input
                  id="new-password"
                  type={showNewPassword ? 'text' : 'password'}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  disabled={loading}
                  required
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  disabled={loading}
                >
                  {showNewPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
              {/* Password requirements (SEC-012) */}
              <div className="text-xs space-y-1">
                <p className="text-muted-foreground">Passwort-Anforderungen:</p>
                <ul className="space-y-0.5 text-muted-foreground">
                  <li className={newPassword.length >= 12 ? 'text-green-600' : ''}>
                    {newPassword.length >= 12 ? '✓' : '○'} Mindestens 12 Zeichen
                  </li>
                  <li className={/[A-Z]/.test(newPassword) ? 'text-green-600' : ''}>
                    {/[A-Z]/.test(newPassword) ? '✓' : '○'} Ein Großbuchstabe
                  </li>
                  <li className={/[a-z]/.test(newPassword) ? 'text-green-600' : ''}>
                    {/[a-z]/.test(newPassword) ? '✓' : '○'} Ein Kleinbuchstabe
                  </li>
                  <li className={/[0-9]/.test(newPassword) ? 'text-green-600' : ''}>
                    {/[0-9]/.test(newPassword) ? '✓' : '○'} Eine Ziffer
                  </li>
                  <li className={/[!@#$%^&*(),.?":{}|<>]/.test(newPassword) ? 'text-green-600' : ''}>
                    {/[!@#$%^&*(),.?":{}|<>]/.test(newPassword) ? '✓' : '○'} Ein Sonderzeichen
                  </li>
                </ul>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm-password">Neues Passwort bestätigen</Label>
              <div className="relative">
                <Input
                  id="confirm-password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  disabled={loading}
                  required
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  disabled={loading}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
              {confirmPassword && !passwordsMatch && (
                <p className="text-xs text-destructive">
                  Passwörter stimmen nicht überein
                </p>
              )}
              {confirmPassword && passwordsMatch && (
                <p className="text-xs text-green-600">
                  ✓ Passwörter stimmen überein
                </p>
              )}
            </div>

            <Button
              type="submit"
              disabled={loading || passwordErrors.length > 0 || !passwordsMatch || !currentPassword}
            >
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Passwort ändern
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Two-Factor Authentication */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5" />
            Zwei-Faktor-Authentifizierung
          </CardTitle>
          <CardDescription>
            Fügen Sie Ihrem Konto eine zusätzliche Sicherheitsebene hinzu
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <div className="text-sm font-medium">
                Zwei-Faktor-Authentifizierung aktivieren
              </div>
              <div className="text-sm text-muted-foreground">
                Erfordert einen Verifizierungscode zusätzlich zu Ihrem Passwort
              </div>
            </div>
            <Switch
              checked={twoFactorEnabled}
              onCheckedChange={handle2FAToggle}
            />
          </div>

          {twoFactorEnabled && (
            <>
              <Separator className="my-4" />
              <div className="text-sm text-muted-foreground">
                <p className="mb-2">
                  Zwei-Faktor-Authentifizierung ist für Ihr Konto aktiviert.
                </p>
                <Button variant="outline" size="sm">
                  Wiederherstellungscodes anzeigen
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
