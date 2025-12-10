/**
 * SEC-005: Secure Usage Stats Hook
 *
 * SECURITY IMPROVEMENTS:
 * - Removed localStorage token storage (XSS vulnerable)
 * - Uses centralized API client with Supabase session
 * - Proper error handling with typed responses
 */

import { useState, useEffect, useCallback } from 'react'
import { api, getAuthToken } from '@/lib/api'

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

export function useUsageStats(params: UseUsageStatsParams = {}) {
  const [stats, setStats] = useState<UsageStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  // Memoize params to avoid unnecessary re-fetches
  const paramsKey = JSON.stringify({
    dateRange: params.dateRange,
    apiKeyId: params.apiKeyId,
    startDate: params.startDate?.toISOString(),
    endDate: params.endDate?.toISOString(),
  })

  const fetchStats = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // Build query parameters
      const queryParams: Record<string, string> = {}
      if (params.dateRange) queryParams.range = params.dateRange
      if (params.apiKeyId) queryParams.license_id = params.apiKeyId
      if (params.startDate)
        queryParams.start_date = params.startDate.toISOString()
      if (params.endDate) queryParams.end_date = params.endDate.toISOString()

      // SEC-005: Use centralized API client with secure auth
      const data = await api.getUsageStats(queryParams)
      setStats(data as UsageStats)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [paramsKey]) // eslint-disable-line react-hooks/exhaustive-deps

  const exportToCsv = useCallback(async (): Promise<Blob> => {
    // Build query parameters
    const exportParams: Record<string, string> = { format: 'csv' }
    if (params.dateRange) exportParams.range = params.dateRange
    if (params.startDate)
      exportParams.start_date = params.startDate.toISOString()
    if (params.endDate) exportParams.end_date = params.endDate.toISOString()

    // SEC-005: Use centralized API client with secure auth
    return await api.exportUsageData(exportParams)
  }, [params.dateRange, params.startDate, params.endDate])

  useEffect(() => {
    fetchStats()
  }, [fetchStats])

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
    exportToCsv,
  }
}
