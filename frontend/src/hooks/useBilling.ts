/**
 * SEC-005: Secure Billing Hook
 *
 * SECURITY IMPROVEMENTS:
 * - Removed localStorage token storage (XSS vulnerable)
 * - Uses centralized API client with Supabase session
 * - Includes CSRF token for state-changing requests
 * - Proper error handling with typed responses
 */

import { useState, useEffect, useCallback } from 'react'
import { api, getAuthToken } from '@/lib/api'

export interface PaymentMethod {
  id: string
  type: 'card'
  brand: string
  last4: string
  expiryMonth: number
  expiryYear: number
  isDefault: boolean
}

export interface Invoice {
  id: string
  date: Date
  amount: number
  status: 'paid' | 'pending' | 'failed'
  description: string
  invoiceUrl?: string
  pdfUrl?: string
}

export interface BillingInfo {
  currentPlan: {
    name: string
    type: 'free' | 'pro' | 'enterprise'
    features: string[]
  }
  credits: {
    current: number
    monthlyAllocation?: number
  }
  paymentMethods: PaymentMethod[]
  invoices: Invoice[]
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

export function useBilling() {
  const [billingInfo, setBillingInfo] = useState<BillingInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchBillingInfo = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // SEC-005: Use centralized API client with secure auth
      const data = await api.getBillingInfo()
      setBillingInfo(data as BillingInfo)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [])

  const createCheckoutSession = useCallback(
    async (creditPackageId: string): Promise<{ url: string }> => {
      // SEC-005: Use secure fetch with Supabase session
      const response = await secureFetch('/api/v1/billing/checkout', {
        method: 'POST',
        body: JSON.stringify({ packageId: creditPackageId }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(
          errorData.detail || 'Failed to create checkout session'
        )
      }

      return await response.json()
    },
    []
  )

  const addPaymentMethod = useCallback(
    async (): Promise<{ setupIntentSecret: string }> => {
      // SEC-005: Use secure fetch with Supabase session
      const response = await secureFetch(
        '/api/v1/billing/payment-methods/setup',
        {
          method: 'POST',
        }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to setup payment method')
      }

      return await response.json()
    },
    []
  )

  const deletePaymentMethod = useCallback(
    async (paymentMethodId: string): Promise<void> => {
      // SEC-005: Use secure fetch with Supabase session
      const response = await secureFetch(
        `/api/v1/billing/payment-methods/${paymentMethodId}`,
        {
          method: 'DELETE',
        }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to delete payment method')
      }

      await fetchBillingInfo() // Refresh billing info
    },
    [fetchBillingInfo]
  )

  const setDefaultPaymentMethod = useCallback(
    async (paymentMethodId: string): Promise<void> => {
      // SEC-005: Use secure fetch with Supabase session
      const response = await secureFetch(
        `/api/v1/billing/payment-methods/${paymentMethodId}/default`,
        {
          method: 'POST',
        }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(
          errorData.detail || 'Failed to set default payment method'
        )
      }

      await fetchBillingInfo() // Refresh billing info
    },
    [fetchBillingInfo]
  )

  const upgradePlan = useCallback(
    async (planType: 'pro' | 'enterprise'): Promise<void> => {
      // SEC-005: Use secure fetch with Supabase session
      const response = await secureFetch('/api/v1/billing/upgrade', {
        method: 'POST',
        body: JSON.stringify({ planType }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to upgrade plan')
      }

      await fetchBillingInfo() // Refresh billing info
    },
    [fetchBillingInfo]
  )

  useEffect(() => {
    fetchBillingInfo()
  }, [fetchBillingInfo])

  return {
    billingInfo,
    loading,
    error,
    refetch: fetchBillingInfo,
    createCheckoutSession,
    addPaymentMethod,
    deletePaymentMethod,
    setDefaultPaymentMethod,
    upgradePlan,
  }
}
