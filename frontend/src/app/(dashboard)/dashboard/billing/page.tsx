'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { PlanCard } from '@/components/dashboard/billing/PlanCard'
import { CreditBalance } from '@/components/dashboard/billing/CreditBalance'
import { PaymentMethods, type PaymentMethod } from '@/components/dashboard/billing/PaymentMethods'
import { InvoicesTable, type Invoice } from '@/components/dashboard/billing/InvoicesTable'
import { AddCreditsDialog } from '@/components/dashboard/billing/AddCreditsDialog'

// Mock data - TODO: Replace with actual API calls
const mockPaymentMethods: PaymentMethod[] = [
  {
    id: '1',
    type: 'card',
    brand: 'visa',
    last4: '4242',
    expiryMonth: 12,
    expiryYear: 2025,
    isDefault: true,
  },
  {
    id: '2',
    type: 'card',
    brand: 'mastercard',
    last4: '5555',
    expiryMonth: 8,
    expiryYear: 2026,
    isDefault: false,
  },
]

const mockInvoices: Invoice[] = [
  {
    id: '1',
    date: new Date(2024, 11, 1),
    amount: 4500,
    status: 'paid',
    description: 'Credit Top-up - 5000 credits',
    invoiceUrl: '#',
    pdfUrl: '#',
  },
  {
    id: '2',
    date: new Date(2024, 10, 1),
    amount: 10000,
    status: 'paid',
    description: 'Pro Plan - Monthly',
    invoiceUrl: '#',
    pdfUrl: '#',
  },
  {
    id: '3',
    date: new Date(2024, 9, 1),
    amount: 10000,
    status: 'paid',
    description: 'Pro Plan - Monthly',
    invoiceUrl: '#',
    pdfUrl: '#',
  },
]

export default function BillingPage() {
  const [loading, setLoading] = useState(true)
  const [addCreditsOpen, setAddCreditsOpen] = useState(false)
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([])
  const [invoices, setInvoices] = useState<Invoice[]>([])

  useEffect(() => {
    // TODO: Fetch from API
    setTimeout(() => {
      setPaymentMethods(mockPaymentMethods)
      setInvoices(mockInvoices)
      setLoading(false)
    }, 500)
  }, [])

  const handleAddPaymentMethod = () => {
    // TODO: Integrate with Stripe
  }

  const handleDeletePaymentMethod = (id: string) => {
    setPaymentMethods((prev) => prev.filter((method) => method.id !== id))
  }

  const handleSetDefaultPaymentMethod = (id: string) => {
    setPaymentMethods((prev) =>
      prev.map((method) => ({
        ...method,
        isDefault: method.id === id,
      }))
    )
  }

  const handleUpgradePlan = () => {
    // TODO: Implement upgrade flow
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-10 w-48 mb-2" />
          <Skeleton className="h-5 w-96" />
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
        <Skeleton className="h-96" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Billing</h1>
        <p className="text-muted-foreground">
          Manage your subscription, credits, and payment methods
        </p>
      </div>

      {/* Plan and Credits */}
      <div className="grid gap-6 md:grid-cols-2">
        <PlanCard
          planName="Pro Plan"
          planType="pro"
          features={[
            '100,000 credits per month',
            'Access to all AI models',
            'Priority support',
            'Advanced analytics',
            'Custom integrations',
          ]}
          onUpgrade={handleUpgradePlan}
        />

        <CreditBalance
          currentCredits={12450}
          monthlyAllocation={100000}
          onAddCredits={() => setAddCreditsOpen(true)}
        />
      </div>

      {/* Payment Methods */}
      <PaymentMethods
        paymentMethods={paymentMethods}
        onAdd={handleAddPaymentMethod}
        onDelete={handleDeletePaymentMethod}
        onSetDefault={handleSetDefaultPaymentMethod}
      />

      {/* Invoices */}
      <Card>
        <CardHeader>
          <CardTitle>Invoices</CardTitle>
          <CardDescription>
            Your billing history and invoices
          </CardDescription>
        </CardHeader>
        <CardContent>
          <InvoicesTable invoices={invoices} />
        </CardContent>
      </Card>

      {/* Add Credits Dialog */}
      <AddCreditsDialog
        open={addCreditsOpen}
        onOpenChange={setAddCreditsOpen}
        onSuccess={() => {
          // TODO: Refresh credit balance
        }}
      />
    </div>
  )
}
