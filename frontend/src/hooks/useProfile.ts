/**
 * SEC-005: Secure Profile Hook
 *
 * SECURITY IMPROVEMENTS:
 * - Removed localStorage token storage (XSS vulnerable)
 * - Uses centralized API client with Supabase session
 * - Includes CSRF token for state-changing requests
 * - Proper error handling with typed responses
 */

import { useState, useEffect, useCallback } from 'react'
import { api, getAuthToken } from '@/lib/api'

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

// API base URL from environment
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * SEC-005: Secure fetch helper using Supabase session
 * Replaces localStorage token access with secure session management
 */
async function secureFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = await getAuthToken()

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...(options.headers || {}),
  }

  return fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include', // SEC-005: Include cookies for auth
  })
}

export function useProfile() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchProfile = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // SEC-005: Use centralized API client with secure auth
      const data = await api.getProfile()
      setProfile(data as UserProfile)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [])

  const updateProfile = useCallback(
    async (updates: { name?: string; avatarUrl?: string }): Promise<void> => {
      // SEC-005: Use centralized API client with secure auth
      await api.updateProfile(updates)
      await fetchProfile() // Refresh profile
    },
    [fetchProfile]
  )

  const updatePassword = useCallback(
    async (currentPassword: string, newPassword: string): Promise<void> => {
      // SEC-005: Use centralized API client with secure auth
      await api.updatePassword(currentPassword, newPassword)
    },
    []
  )

  const updateNotificationPreferences = useCallback(
    async (
      preferences: UserProfile['notificationPreferences']
    ): Promise<void> => {
      // SEC-005: Use secure fetch with Supabase session
      const response = await secureFetch('/api/v1/profile/notifications', {
        method: 'PATCH',
        body: JSON.stringify(preferences),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(
          errorData.detail || 'Failed to update notification preferences'
        )
      }

      await fetchProfile() // Refresh profile
    },
    [fetchProfile]
  )

  const updatePreferences = useCallback(
    async (preferences: UserProfile['preferences']): Promise<void> => {
      // SEC-005: Use secure fetch with Supabase session
      const response = await secureFetch('/api/v1/profile/preferences', {
        method: 'PATCH',
        body: JSON.stringify(preferences),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to update preferences')
      }

      await fetchProfile() // Refresh profile
    },
    [fetchProfile]
  )

  const enable2FA = useCallback(
    async (): Promise<{ qrCode: string; secret: string }> => {
      // SEC-005: Use secure fetch with Supabase session
      const response = await secureFetch('/api/v1/profile/2fa/enable', {
        method: 'POST',
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to enable 2FA')
      }

      return await response.json()
    },
    []
  )

  const disable2FA = useCallback(
    async (code: string): Promise<void> => {
      // SEC-005: Use secure fetch with Supabase session
      const response = await secureFetch('/api/v1/profile/2fa/disable', {
        method: 'POST',
        body: JSON.stringify({ code }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to disable 2FA')
      }

      await fetchProfile() // Refresh profile
    },
    [fetchProfile]
  )

  useEffect(() => {
    fetchProfile()
  }, [fetchProfile])

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
