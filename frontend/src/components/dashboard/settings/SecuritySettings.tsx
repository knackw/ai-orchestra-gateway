'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import { Loader2, ShieldCheck } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface SecuritySettingsProps {
  twoFactorEnabled: boolean
  onUpdate: (data: { twoFactorEnabled: boolean }) => Promise<void>
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
  const { toast } = useToast()

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()

    if (newPassword !== confirmPassword) {
      toast({
        title: 'Error',
        description: 'New passwords do not match.',
        variant: 'destructive',
      })
      return
    }

    if (newPassword.length < 8) {
      toast({
        title: 'Error',
        description: 'Password must be at least 8 characters long.',
        variant: 'destructive',
      })
      return
    }

    setLoading(true)
    try {
      // TODO: Call API to change password
      await new Promise((resolve) => setTimeout(resolve, 1000))

      toast({
        title: 'Password Changed',
        description: 'Your password has been updated successfully.',
      })

      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to change password.',
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
        title: enabled ? '2FA Enabled' : '2FA Disabled',
        description: enabled
          ? 'Two-factor authentication has been enabled.'
          : 'Two-factor authentication has been disabled.',
      })
    } catch {
      setTwoFactorEnabled(!enabled)
      toast({
        title: 'Error',
        description: 'Failed to update 2FA settings.',
        variant: 'destructive',
      })
    }
  }

  return (
    <div className="space-y-6">
      {/* Change Password */}
      <Card>
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
          <CardDescription>
            Update your password to keep your account secure
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="current-password">Current Password</Label>
              <Input
                id="current-password"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                disabled={loading}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="new-password">New Password</Label>
              <Input
                id="new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                disabled={loading}
                required
              />
              <p className="text-xs text-muted-foreground">
                Must be at least 8 characters long
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm-password">Confirm New Password</Label>
              <Input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading}
                required
              />
            </div>

            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Change Password
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Two-Factor Authentication */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5" />
            Two-Factor Authentication
          </CardTitle>
          <CardDescription>
            Add an extra layer of security to your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <div className="text-sm font-medium">
                Enable Two-Factor Authentication
              </div>
              <div className="text-sm text-muted-foreground">
                Require a verification code in addition to your password
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
                  Two-factor authentication is currently enabled for your account.
                </p>
                <Button variant="outline" size="sm">
                  View Recovery Codes
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
