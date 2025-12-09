'use client'

import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  User,
  Shield,
  Bell,
  Settings as SettingsIcon,
  AlertTriangle,
  Upload,
  CheckCircle,
  LogOut,
  Smartphone,
} from 'lucide-react'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'

export default function SettingsPage() {
  // Profile state
  const [profileData, setProfileData] = useState({
    name: 'John Doe',
    email: 'john@example.com',
    company: 'Acme Corp',
    avatarUrl: undefined as string | undefined,
  })
  const [profileSaving, setProfileSaving] = useState(false)

  // Security state
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false)
  const [securitySaving, setSecuritySaving] = useState(false)
  const [activeSessions] = useState([
    { id: '1', device: 'Chrome on MacOS', location: 'Berlin, Germany', lastActive: '2 minutes ago', current: true },
    { id: '2', device: 'Safari on iPhone', location: 'Berlin, Germany', lastActive: '1 hour ago', current: false },
    { id: '3', device: 'Firefox on Windows', location: 'Munich, Germany', lastActive: '2 days ago', current: false },
  ])

  // Notification state
  const [notifications, setNotifications] = useState({
    emailOnNewApiKey: true,
    emailOnCreditLow: true,
    emailOnCreditPurchase: true,
    emailOnInvoice: true,
    emailOnSecurityAlert: true,
    emailOnProductUpdates: false,
    emailOnMarketingOffers: false,
  })
  const [notificationsSaving, setNotificationsSaving] = useState(false)

  // API Settings state
  const [apiSettings, setApiSettings] = useState({
    defaultProvider: 'anthropic',
    rateLimit: '60',
  })
  const [apiSettingsSaving, setApiSettingsSaving] = useState(false)

  // Handlers
  const handleProfileSave = async () => {
    setProfileSaving(true)
    // TODO: Call API to save profile
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setProfileSaving(false)
  }

  const handlePasswordChange = async () => {
    // TODO: Implement password change
    await new Promise((resolve) => setTimeout(resolve, 1000))
  }

  const handleTwoFactorToggle = async () => {
    setSecuritySaving(true)
    // TODO: Call API to toggle 2FA
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setTwoFactorEnabled(!twoFactorEnabled)
    setSecuritySaving(false)
  }

  const handleRevokeSession = async (sessionId: string) => {
    // TODO: Call API to revoke session
    console.log('Revoke session:', sessionId)
  }

  const handleNotificationsSave = async () => {
    setNotificationsSaving(true)
    // TODO: Call API to save notifications
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setNotificationsSaving(false)
  }

  const handleApiSettingsSave = async () => {
    setApiSettingsSaving(true)
    // TODO: Call API to save API settings
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setApiSettingsSaving(false)
  }

  const handleDeleteAccount = async () => {
    // TODO: Implement account deletion
    console.log('Delete account')
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
          <TabsTrigger value="profile" className="gap-2">
            <User className="h-4 w-4" />
            <span className="hidden sm:inline">Profile</span>
          </TabsTrigger>
          <TabsTrigger value="security" className="gap-2">
            <Shield className="h-4 w-4" />
            <span className="hidden sm:inline">Security</span>
          </TabsTrigger>
          <TabsTrigger value="notifications" className="gap-2">
            <Bell className="h-4 w-4" />
            <span className="hidden sm:inline">Notifications</span>
          </TabsTrigger>
          <TabsTrigger value="api" className="gap-2">
            <SettingsIcon className="h-4 w-4" />
            <span className="hidden sm:inline">API Settings</span>
          </TabsTrigger>
          <TabsTrigger value="danger" className="gap-2">
            <AlertTriangle className="h-4 w-4" />
            <span className="hidden sm:inline">Danger Zone</span>
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>
                Update your account profile information and email address
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Avatar */}
              <div className="flex items-center gap-4">
                <Avatar className="h-20 w-20">
                  <AvatarImage src={profileData.avatarUrl} alt={profileData.name} />
                  <AvatarFallback className="text-2xl">
                    {profileData.name
                      .split(' ')
                      .map((n) => n[0])
                      .join('')}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <Button variant="outline" size="sm">
                    <Upload className="mr-2 h-4 w-4" />
                    Change Avatar
                  </Button>
                  <p className="text-xs text-muted-foreground mt-2">
                    JPG, PNG or GIF. Max size 2MB.
                  </p>
                </div>
              </div>

              <Separator />

              {/* Name */}
              <div className="grid gap-2">
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  value={profileData.name}
                  onChange={(e) =>
                    setProfileData({ ...profileData, name: e.target.value })
                  }
                />
              </div>

              {/* Email */}
              <div className="grid gap-2">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  value={profileData.email}
                  onChange={(e) =>
                    setProfileData({ ...profileData, email: e.target.value })
                  }
                />
                <p className="text-xs text-muted-foreground">
                  This email will be used for notifications and account recovery
                </p>
              </div>

              {/* Company */}
              <div className="grid gap-2">
                <Label htmlFor="company">Company (Optional)</Label>
                <Input
                  id="company"
                  value={profileData.company}
                  onChange={(e) =>
                    setProfileData({ ...profileData, company: e.target.value })
                  }
                />
              </div>

              <Button onClick={handleProfileSave} disabled={profileSaving}>
                {profileSaving ? 'Saving...' : 'Save Changes'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security" className="space-y-4">
          {/* Password */}
          <Card>
            <CardHeader>
              <CardTitle>Password</CardTitle>
              <CardDescription>
                Change your password to keep your account secure
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-2">
                <Label htmlFor="current-password">Current Password</Label>
                <Input id="current-password" type="password" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="new-password">New Password</Label>
                <Input id="new-password" type="password" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="confirm-password">Confirm New Password</Label>
                <Input id="confirm-password" type="password" />
              </div>
              <Button onClick={handlePasswordChange}>Change Password</Button>
            </CardContent>
          </Card>

          {/* Two-Factor Authentication */}
          <Card>
            <CardHeader>
              <CardTitle>Two-Factor Authentication</CardTitle>
              <CardDescription>
                Add an extra layer of security to your account
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <Label>Two-Factor Authentication</Label>
                    {twoFactorEnabled && (
                      <Badge variant="outline" className="gap-1">
                        <CheckCircle className="h-3 w-3" />
                        Enabled
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {twoFactorEnabled
                      ? 'Your account is protected with 2FA'
                      : 'Use an authenticator app to generate verification codes'}
                  </p>
                </div>
                <Switch
                  checked={twoFactorEnabled}
                  onCheckedChange={handleTwoFactorToggle}
                  disabled={securitySaving}
                />
              </div>
              {twoFactorEnabled && (
                <Alert>
                  <Smartphone className="h-4 w-4" />
                  <AlertTitle>Authenticator App Connected</AlertTitle>
                  <AlertDescription>
                    You will be asked for a verification code when signing in.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Active Sessions */}
          <Card>
            <CardHeader>
              <CardTitle>Active Sessions</CardTitle>
              <CardDescription>
                Manage devices where you are currently signed in
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {activeSessions.map((session) => (
                  <div
                    key={session.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{session.device}</p>
                        {session.current && (
                          <Badge variant="secondary">Current Session</Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {session.location} • {session.lastActive}
                      </p>
                    </div>
                    {!session.current && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRevokeSession(session.id)}
                      >
                        <LogOut className="h-4 w-4 mr-2" />
                        Revoke
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Email Notifications</CardTitle>
              <CardDescription>
                Choose which emails you want to receive
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>New API Key Created</Label>
                    <p className="text-sm text-muted-foreground">
                      Get notified when a new API key is created
                    </p>
                  </div>
                  <Switch
                    checked={notifications.emailOnNewApiKey}
                    onCheckedChange={(checked) =>
                      setNotifications({ ...notifications, emailOnNewApiKey: checked })
                    }
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Low Credit Balance</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive alerts when your credit balance is running low
                    </p>
                  </div>
                  <Switch
                    checked={notifications.emailOnCreditLow}
                    onCheckedChange={(checked) =>
                      setNotifications({ ...notifications, emailOnCreditLow: checked })
                    }
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Credit Purchase</Label>
                    <p className="text-sm text-muted-foreground">
                      Confirmation emails for credit purchases
                    </p>
                  </div>
                  <Switch
                    checked={notifications.emailOnCreditPurchase}
                    onCheckedChange={(checked) =>
                      setNotifications({
                        ...notifications,
                        emailOnCreditPurchase: checked,
                      })
                    }
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Invoice Available</Label>
                    <p className="text-sm text-muted-foreground">
                      Get notified when a new invoice is ready
                    </p>
                  </div>
                  <Switch
                    checked={notifications.emailOnInvoice}
                    onCheckedChange={(checked) =>
                      setNotifications({ ...notifications, emailOnInvoice: checked })
                    }
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Security Alerts</Label>
                    <p className="text-sm text-muted-foreground">
                      Important security notifications (recommended)
                    </p>
                  </div>
                  <Switch
                    checked={notifications.emailOnSecurityAlert}
                    onCheckedChange={(checked) =>
                      setNotifications({
                        ...notifications,
                        emailOnSecurityAlert: checked,
                      })
                    }
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Product Updates</Label>
                    <p className="text-sm text-muted-foreground">
                      News about new features and improvements
                    </p>
                  </div>
                  <Switch
                    checked={notifications.emailOnProductUpdates}
                    onCheckedChange={(checked) =>
                      setNotifications({
                        ...notifications,
                        emailOnProductUpdates: checked,
                      })
                    }
                  />
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Marketing Offers</Label>
                    <p className="text-sm text-muted-foreground">
                      Special offers and promotional content
                    </p>
                  </div>
                  <Switch
                    checked={notifications.emailOnMarketingOffers}
                    onCheckedChange={(checked) =>
                      setNotifications({
                        ...notifications,
                        emailOnMarketingOffers: checked,
                      })
                    }
                  />
                </div>
              </div>

              <Button onClick={handleNotificationsSave} disabled={notificationsSaving}>
                {notificationsSaving ? 'Saving...' : 'Save Preferences'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Settings Tab */}
        <TabsContent value="api" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>API Settings</CardTitle>
              <CardDescription>
                Configure default settings for your API requests
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-2">
                <Label htmlFor="default-provider">Default AI Provider</Label>
                <Select
                  value={apiSettings.defaultProvider}
                  onValueChange={(value) =>
                    setApiSettings({ ...apiSettings, defaultProvider: value })
                  }
                >
                  <SelectTrigger id="default-provider">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="anthropic">Anthropic (Claude)</SelectItem>
                    <SelectItem value="scaleway">Scaleway AI</SelectItem>
                    <SelectItem value="auto">Auto (Best Available)</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  This will be used when no provider is specified in the request
                </p>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="rate-limit">Rate Limit (requests per minute)</Label>
                <Select
                  value={apiSettings.rateLimit}
                  onValueChange={(value) =>
                    setApiSettings({ ...apiSettings, rateLimit: value })
                  }
                >
                  <SelectTrigger id="rate-limit">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="30">30 requests/min</SelectItem>
                    <SelectItem value="60">60 requests/min</SelectItem>
                    <SelectItem value="120">120 requests/min</SelectItem>
                    <SelectItem value="unlimited">Unlimited</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  Maximum number of API requests per minute per API key
                </p>
              </div>

              <Button onClick={handleApiSettingsSave} disabled={apiSettingsSaving}>
                {apiSettingsSaving ? 'Saving...' : 'Save Settings'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Danger Zone Tab */}
        <TabsContent value="danger" className="space-y-4">
          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">Danger Zone</CardTitle>
              <CardDescription>
                Irreversible actions that will affect your account
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Warning</AlertTitle>
                <AlertDescription>
                  The following actions cannot be undone. Please proceed with caution.
                </AlertDescription>
              </Alert>

              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border border-destructive rounded-lg">
                  <div className="space-y-1">
                    <p className="font-medium">Delete Account</p>
                    <p className="text-sm text-muted-foreground">
                      Permanently delete your account and all associated data
                    </p>
                  </div>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="destructive">Delete Account</Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This action cannot be undone. This will permanently delete your
                          account and remove all of your data from our servers, including:
                          <ul className="list-disc list-inside mt-2 space-y-1">
                            <li>All API keys</li>
                            <li>Usage history and analytics</li>
                            <li>Billing information</li>
                            <li>Remaining credits</li>
                          </ul>
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={handleDeleteAccount}
                          className="bg-destructive hover:bg-destructive/90"
                        >
                          Yes, Delete My Account
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
