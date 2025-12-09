import { useState, useEffect } from 'react'

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

  const fetchApiKeys = async () => {
    setLoading(true)
    setError(null)
    try {
      // TODO: Replace with actual API call
      const response = await fetch('/api/v1/api-keys', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to fetch API keys')
      }

      const data = await response.json()
      setApiKeys(data)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }

  const createApiKey = async (name: string): Promise<{ key: string; id: string }> => {
    // TODO: Replace with actual API call
    const response = await fetch('/api/v1/api-keys', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ name }),
    })

    if (!response.ok) {
      throw new Error('Failed to create API key')
    }

    const data = await response.json()
    await fetchApiKeys() // Refresh the list
    return data
  }

  const deleteApiKey = async (id: string): Promise<void> => {
    // TODO: Replace with actual API call
    const response = await fetch(`/api/v1/api-keys/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to delete API key')
    }

    await fetchApiKeys() // Refresh the list
  }

  const rotateApiKey = async (id: string): Promise<{ key: string }> => {
    // TODO: Replace with actual API call
    const response = await fetch(`/api/v1/api-keys/${id}/rotate`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to rotate API key')
    }

    const data = await response.json()
    await fetchApiKeys() // Refresh the list
    return data
  }

  useEffect(() => {
    fetchApiKeys()
  }, [])

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
