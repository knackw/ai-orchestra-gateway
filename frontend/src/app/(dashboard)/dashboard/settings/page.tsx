'use client'

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ProfileForm } from '@/components/dashboard/settings/ProfileForm'
import { SecuritySettings } from '@/components/dashboard/settings/SecuritySettings'
import { NotificationSettings } from '@/components/dashboard/settings/NotificationSettings'
import { PreferencesSettings } from '@/components/dashboard/settings/PreferencesSettings'
import { ApiSettings } from '@/components/dashboard/settings/ApiSettings'

export default function SettingsPage() {
  // Mock data - TODO: Fetch from API
  const profileData = {
    name: 'John Doe',
    email: 'john@example.com',
    avatarUrl: undefined,
  }

  const notificationPreferences = {
    emailOnNewApiKey: true,
    emailOnCreditLow: true,
    emailOnCreditPurchase: true,
    emailOnInvoice: true,
    emailOnSecurityAlert: true,
    emailOnProductUpdates: false,
    emailOnMarketingOffers: false,
  }

  const userPreferences = {
    language: 'en',
    timezone: 'UTC',
  }

  const apiSettings = {
    defaultProvider: 'anthropic',
    euOnlyMode: false,
    rateLimitPerMinute: 60,
    webhookUrl: undefined,
  }

  const handleProfileUpdate = async (data: { name: string; email: string; avatarUrl?: string }) => {
    // TODO: Call API to update profile
    void data // SEC-016: Prevent unused variable warning
    await new Promise((resolve) => setTimeout(resolve, 1000))
  }

  const handleSecurityUpdate = async (data: { twoFactorEnabled: boolean }) => {
    // TODO: Call API to update security settings
    void data // SEC-016: Prevent unused variable warning
    await new Promise((resolve) => setTimeout(resolve, 500))
  }

  const handleNotificationUpdate = async (
    preferences: typeof notificationPreferences
  ) => {
    // TODO: Call API to update notification preferences
    void preferences // SEC-016: Prevent unused variable warning
    await new Promise((resolve) => setTimeout(resolve, 500))
  }

  const handlePreferencesUpdate = async (
    preferences: typeof userPreferences
  ) => {
    // TODO: Call API to update user preferences
    void preferences // SEC-016: Prevent unused variable warning
    await new Promise((resolve) => setTimeout(resolve, 1000))
  }

  const handleApiSettingsUpdate = async (
    settings: typeof apiSettings
  ) => {
    // TODO: Call API to update API settings
    void settings // SEC-016: Prevent unused variable warning
    await new Promise((resolve) => setTimeout(resolve, 1000))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Manage your account settings and preferences
        </p>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5 lg:w-auto">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="api">API Settings</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="space-y-4">
          <ProfileForm
            initialData={profileData}
            onUpdate={handleProfileUpdate}
          />
        </TabsContent>

        <TabsContent value="security" className="space-y-4">
          <SecuritySettings
            twoFactorEnabled={false}
            onUpdate={handleSecurityUpdate}
          />
        </TabsContent>

        <TabsContent value="api" className="space-y-4">
          <ApiSettings
            initialSettings={apiSettings}
            onUpdate={handleApiSettingsUpdate}
          />
        </TabsContent>

        <TabsContent value="notifications" className="space-y-4">
          <NotificationSettings
            initialPreferences={notificationPreferences}
            onUpdate={handleNotificationUpdate}
          />
        </TabsContent>

        <TabsContent value="preferences" className="space-y-4">
          <PreferencesSettings
            initialPreferences={userPreferences}
            onUpdate={handlePreferencesUpdate}
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}
