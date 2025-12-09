'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { useToast } from '@/hooks/use-toast'

interface NotificationPreferences {
  emailOnNewApiKey: boolean
  emailOnCreditLow: boolean
  emailOnCreditPurchase: boolean
  emailOnInvoice: boolean
  emailOnSecurityAlert: boolean
  emailOnProductUpdates: boolean
  emailOnMarketingOffers: boolean
}

interface NotificationSettingsProps {
  initialPreferences: NotificationPreferences
  onUpdate: (preferences: NotificationPreferences) => Promise<void>
}

export function NotificationSettings({
  initialPreferences,
  onUpdate,
}: NotificationSettingsProps) {
  const [preferences, setPreferences] = useState(initialPreferences)
  const { toast } = useToast()

  const handleToggle = async (
    key: keyof NotificationPreferences,
    value: boolean
  ) => {
    const newPreferences = { ...preferences, [key]: value }
    setPreferences(newPreferences)

    try {
      await onUpdate(newPreferences)
      toast({
        title: 'Preferences Updated',
        description: 'Your notification preferences have been saved.',
      })
    } catch {
      // Revert on error
      setPreferences(preferences)
      toast({
        title: 'Error',
        description: 'Failed to update notification preferences.',
        variant: 'destructive',
      })
    }
  }

  const NotificationToggle = ({
    id,
    label,
    description,
  }: {
    id: keyof NotificationPreferences
    label: string
    description: string
  }) => (
    <div className="flex items-center justify-between space-x-2">
      <Label htmlFor={id} className="flex flex-col space-y-1 flex-1 cursor-pointer">
        <span className="font-medium">{label}</span>
        <span className="text-sm text-muted-foreground font-normal">
          {description}
        </span>
      </Label>
      <Switch
        id={id}
        checked={preferences[id]}
        onCheckedChange={(checked) => handleToggle(id, checked)}
      />
    </div>
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle>Email Notifications</CardTitle>
        <CardDescription>
          Choose which emails you want to receive
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Account & Security */}
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-semibold mb-3">Account & Security</h3>
            <div className="space-y-4">
              <NotificationToggle
                id="emailOnNewApiKey"
                label="New API Key Created"
                description="Get notified when a new API key is created"
              />
              <NotificationToggle
                id="emailOnSecurityAlert"
                label="Security Alerts"
                description="Important security updates and alerts"
              />
            </div>
          </div>
        </div>

        <Separator />

        {/* Billing */}
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-semibold mb-3">Billing & Credits</h3>
            <div className="space-y-4">
              <NotificationToggle
                id="emailOnCreditLow"
                label="Low Credit Balance"
                description="Alert when your credit balance is running low"
              />
              <NotificationToggle
                id="emailOnCreditPurchase"
                label="Credit Purchases"
                description="Confirmation emails for credit purchases"
              />
              <NotificationToggle
                id="emailOnInvoice"
                label="New Invoices"
                description="Get notified when a new invoice is available"
              />
            </div>
          </div>
        </div>

        <Separator />

        {/* Marketing */}
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-semibold mb-3">Updates & Marketing</h3>
            <div className="space-y-4">
              <NotificationToggle
                id="emailOnProductUpdates"
                label="Product Updates"
                description="New features, improvements, and announcements"
              />
              <NotificationToggle
                id="emailOnMarketingOffers"
                label="Marketing & Offers"
                description="Special offers, tips, and promotional emails"
              />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
