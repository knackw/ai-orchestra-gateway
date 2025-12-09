import { useState, useEffect } from 'react'

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

export function useBilling() {
  const [billingInfo, setBillingInfo] = useState<BillingInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchBillingInfo = async () => {
    setLoading(true)
    setError(null)
    try {
      // TODO: Replace with actual API call
      const response = await fetch('/api/v1/billing', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to fetch billing information')
      }

      const data = await response.json()
      setBillingInfo(data)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }

  const createCheckoutSession = async (
    creditPackageId: string
  ): Promise<{ url: string }> => {
    // TODO: Replace with actual API call to create Stripe checkout session
    const response = await fetch('/api/v1/billing/checkout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ packageId: creditPackageId }),
    })

    if (!response.ok) {
      throw new Error('Failed to create checkout session')
    }

    return await response.json()
  }

  const addPaymentMethod = async (): Promise<{ setupIntentSecret: string }> => {
    // TODO: Replace with actual API call to create Stripe SetupIntent
    const response = await fetch('/api/v1/billing/payment-methods/setup', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to setup payment method')
    }

    return await response.json()
  }

  const deletePaymentMethod = async (paymentMethodId: string): Promise<void> => {
    // TODO: Replace with actual API call
    const response = await fetch(
      `/api/v1/billing/payment-methods/${paymentMethodId}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      }
    )

    if (!response.ok) {
      throw new Error('Failed to delete payment method')
    }

    await fetchBillingInfo() // Refresh billing info
  }

  const setDefaultPaymentMethod = async (
    paymentMethodId: string
  ): Promise<void> => {
    // TODO: Replace with actual API call
    const response = await fetch(
      `/api/v1/billing/payment-methods/${paymentMethodId}/default`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      }
    )

    if (!response.ok) {
      throw new Error('Failed to set default payment method')
    }

    await fetchBillingInfo() // Refresh billing info
  }

  const upgradePlan = async (planType: 'pro' | 'enterprise'): Promise<void> => {
    // TODO: Replace with actual API call
    const response = await fetch('/api/v1/billing/upgrade', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ planType }),
    })

    if (!response.ok) {
      throw new Error('Failed to upgrade plan')
    }

    await fetchBillingInfo() // Refresh billing info
  }

  useEffect(() => {
    fetchBillingInfo()
  }, [])

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
