/**
 * SEC-005: Secure API Keys Hook
 *
 * SECURITY IMPROVEMENTS:
 * - Removed localStorage token storage (XSS vulnerable)
 * - Uses centralized API client with Supabase session
 * - Includes CSRF token for state-changing requests
 * - Proper error handling with typed responses
 */

import { useState, useEffect, useCallback } from 'react'
import { api } from '@/lib/api'

export interface ApiKey {
  id: string
  name: string
  key: string
  createdAt: Date
  lastUsed: Date | null
  status: 'active' | 'inactive'
}

export function useApiKeys() {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchApiKeys = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // SEC-005: Use centralized API client with secure auth
      const data = await api.getApiKeys()
      setApiKeys(data as ApiKey[])
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [])

  const createApiKey = useCallback(
    async (name: string): Promise<{ key: string; id: string }> => {
      // SEC-005: Use centralized API client with secure auth
      // Note: The backend expects tenant_id, but for user-facing API this is derived from session
      const data = await api.createApiKey({
        name,
        tenant_id: '', // Will be set by backend from authenticated user context
      })
      await fetchApiKeys() // Refresh the list
      return data as { key: string; id: string }
    },
    [fetchApiKeys]
  )

  const deleteApiKey = useCallback(
    async (id: string): Promise<void> => {
      // SEC-005: Use centralized API client with secure auth
      await api.deleteApiKey(id)
      await fetchApiKeys() // Refresh the list
    },
    [fetchApiKeys]
  )

  const rotateApiKey = useCallback(
    async (id: string): Promise<{ key: string }> => {
      // SEC-005: Use centralized API client with secure auth
      const data = await api.rotateApiKey(id)
      await fetchApiKeys() // Refresh the list
      return data as { key: string }
    },
    [fetchApiKeys]
  )

  useEffect(() => {
    fetchApiKeys()
  }, [fetchApiKeys])

  return {
    apiKeys,
    loading,
    error,
    refetch: fetchApiKeys,
    createApiKey,
    deleteApiKey,
    rotateApiKey,
  }
}
