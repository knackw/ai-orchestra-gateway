import { useState, useEffect } from 'react'

export interface UsageStats {
  requestsData: Array<{
    date: string
    requests: number
    successful?: number
    failed?: number
  }>
  tokensData: Array<{
    date: string
    tokens: number
    inputTokens?: number
    outputTokens?: number
  }>
  creditsData: Array<{
    date: string
    credits: number
  }>
  providerData: Array<{
    name: string
    value: number
  }>
  summary: {
    totalRequests: number
    totalTokens: number
    creditsConsumed: number
    avgResponseTime: number
  }
}

interface UseUsageStatsParams {
  dateRange?: '7d' | '30d' | '90d' | 'custom'
  apiKeyId?: string
  startDate?: Date
  endDate?: Date
}

export function useUsageStats(params: UseUsageStatsParams = {}) {
  const [stats, setStats] = useState<UsageStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchStats = async () => {
    setLoading(true)
    setError(null)
    try {
      // TODO: Replace with actual API call
      const queryParams = new URLSearchParams()
      if (params.dateRange) queryParams.append('range', params.dateRange)
      if (params.apiKeyId) queryParams.append('apiKeyId', params.apiKeyId)
      if (params.startDate)
        queryParams.append('startDate', params.startDate.toISOString())
      if (params.endDate)
        queryParams.append('endDate', params.endDate.toISOString())

      const response = await fetch(`/api/v1/usage/stats?${queryParams}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('_token')}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to fetch usage statistics')
      }

      const data = await response.json()
      setStats(data)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }

  const exportToCsv = async (): Promise<Blob> => {
    // TODO: Replace with actual API call
    const queryParams = new URLSearchParams()
    if (params.dateRange) queryParams.append('range', params.dateRange)
    if (params.apiKeyId) queryParams.append('apiKeyId', params.apiKeyId)

    const response = await fetch(`/api/v1/usage/export?${queryParams}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('_token')}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to export usage data')
    }

    return await response.blob()
  }

  useEffect(() => {
    fetchStats()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    params.dateRange,
    params.apiKeyId,
    params.startDate?.toISOString(),
    params.endDate?.toISOString(),
  ])

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
    exportToCsv,
  }
}
