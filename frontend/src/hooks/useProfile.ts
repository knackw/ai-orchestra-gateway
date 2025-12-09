import { useState, useEffect } from 'react'

export interface UserProfile {
  id: string
  name: string
  email: string
  avatarUrl?: string
  createdAt: Date
  twoFactorEnabled: boolean
  notificationPreferences: {
    emailOnNewApiKey: boolean
    emailOnCreditLow: boolean
    emailOnCreditPurchase: boolean
    emailOnInvoice: boolean
    emailOnSecurityAlert: boolean
    emailOnProductUpdates: boolean
    emailOnMarketingOffers: boolean
  }
  preferences: {
    language: string
    timezone: string
  }
}

export function useProfile() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchProfile = async () => {
    setLoading(true)
    setError(null)
    try {
      // TODO: Replace with actual API call
      const response = await fetch('/api/v1/profile', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to fetch profile')
      }

      const data = await response.json()
      setProfile(data)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }

  const updateProfile = async (updates: {
    name?: string
    avatarUrl?: string
  }): Promise<void> => {
    // TODO: Replace with actual API call
    const response = await fetch('/api/v1/profile', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(updates),
    })

    if (!response.ok) {
      throw new Error('Failed to update profile')
    }

    await fetchProfile() // Refresh profile
  }

  const updatePassword = async (
    currentPassword: string,
    newPassword: string
  ): Promise<void> => {
    // TODO: Replace with actual API call
    const response = await fetch('/api/v1/profile/password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ currentPassword, newPassword }),
    })

    if (!response.ok) {
      throw new Error('Failed to update password')
    }
  }

  const updateNotificationPreferences = async (
    preferences: UserProfile['notificationPreferences']
  ): Promise<void> => {
    // TODO: Replace with actual API call
    const response = await fetch('/api/v1/profile/notifications', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(preferences),
    })

    if (!response.ok) {
      throw new Error('Failed to update notification preferences')
    }

    await fetchProfile() // Refresh profile
  }

  const updatePreferences = async (
    preferences: UserProfile['preferences']
  ): Promise<void> => {
    // TODO: Replace with actual API call
    const response = await fetch('/api/v1/profile/preferences', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(preferences),
    })

    if (!response.ok) {
      throw new Error('Failed to update preferences')
    }

    await fetchProfile() // Refresh profile
  }

  const enable2FA = async (): Promise<{ qrCode: string; secret: string }> => {
    // TODO: Replace with actual API call
    const response = await fetch('/api/v1/profile/2fa/enable', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to enable 2FA')
    }

    return await response.json()
  }

  const disable2FA = async (code: string): Promise<void> => {
    // TODO: Replace with actual API call
    const response = await fetch('/api/v1/profile/2fa/disable', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ code }),
    })

    if (!response.ok) {
      throw new Error('Failed to disable 2FA')
    }

    await fetchProfile() // Refresh profile
  }

  useEffect(() => {
    fetchProfile()
  }, [])

  return {
    profile,
    loading,
    error,
    refetch: fetchProfile,
    updateProfile,
    updatePassword,
    updateNotificationPreferences,
    updatePreferences,
    enable2FA,
    disable2FA,
  }
}
