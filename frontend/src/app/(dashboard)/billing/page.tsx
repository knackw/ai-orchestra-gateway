'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { PlanCard } from '@/components/dashboard/billing/PlanCard'
import { CreditBalance } from '@/components/dashboard/billing/CreditBalance'
import { PaymentMethods, type PaymentMethod } from '@/components/dashboard/billing/PaymentMethods'
import { InvoicesTable, type Invoice } from '@/components/dashboard/billing/InvoicesTable'
import { AddCreditsDialog } from '@/components/dashboard/billing/AddCreditsDialog'
import { AlertCircle, CreditCard, TrendingUp } from 'lucide-react'

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
  {
    id: '4',
    date: new Date(2024, 8, 15),
    amount: 2500,
    status: 'paid',
    description: 'Credit Top-up - 2500 credits',
    invoiceUrl: '#',
    pdfUrl: '#',
  },
]

// Pricing tiers for buying credits
const creditPackages = [
  {
    id: 'starter',
    name: 'Starter Pack',
    credits: 1000,
    price: 10,
    pricePerCredit: 0.01,
  },
  {
    id: 'growth',
    name: 'Growth Pack',
    credits: 5000,
    price: 45,
    pricePerCredit: 0.009,
    popular: true,
  },
  {
    id: 'pro',
    name: 'Pro Pack',
    credits: 10000,
    price: 80,
    pricePerCredit: 0.008,
  },
  {
    id: 'enterprise',
    name: 'Enterprise Pack',
    credits: 50000,
    price: 350,
    pricePerCredit: 0.007,
  },
]

export default function BillingPage() {
  const [loading, setLoading] = useState(true)
  const [addCreditsOpen, setAddCreditsOpen] = useState(false)
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([])
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const currentCredits = 12450
  const monthlyAllocation = 100000
  const lowCreditThreshold = 5000

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
    console.log('Add payment method')
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
    console.log('Upgrade plan')
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
        <Skeleton className="h-48" />
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

      {/* Low Credit Warning */}
      {currentCredits < lowCreditThreshold && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Low Credit Balance</AlertTitle>
          <AlertDescription>
            Your credit balance is running low. Consider topping up to avoid service interruption.
            <Button
              variant="outline"
              size="sm"
              className="ml-4"
              onClick={() => setAddCreditsOpen(true)}
            >
              Buy Credits
            </Button>
          </AlertDescription>
        </Alert>
      )}

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
            'Webhook notifications',
          ]}
          onUpgrade={handleUpgradePlan}
        />

        <CreditBalance
          currentCredits={currentCredits}
          monthlyAllocation={monthlyAllocation}
          onAddCredits={() => setAddCreditsOpen(true)}
        />
      </div>

      {/* Buy Credits Section */}
      <Card>
        <CardHeader>
          <CardTitle>Buy Credits</CardTitle>
          <CardDescription>
            Choose a credit package that fits your needs. Credits never expire.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {creditPackages.map((pkg) => (
              <Card
                key={pkg.id}
                className={pkg.popular ? 'border-primary shadow-md' : ''}
              >
                {pkg.popular && (
                  <div className="px-4 pt-3">
                    <Badge>Most Popular</Badge>
                  </div>
                )}
                <CardHeader>
                  <CardTitle className="text-lg">{pkg.name}</CardTitle>
                  <CardDescription>
                    {pkg.credits.toLocaleString()} credits
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="text-3xl font-bold">
                      ${pkg.price}
                      <span className="text-sm font-normal text-muted-foreground">
                        .00
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      ${pkg.pricePerCredit.toFixed(3)} per credit
                    </p>
                  </div>
                  <Button
                    className="w-full"
                    variant={pkg.popular ? 'default' : 'outline'}
                    onClick={() => setAddCreditsOpen(true)}
                  >
                    <CreditCard className="mr-2 h-4 w-4" />
                    Purchase
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="mt-4 p-4 bg-muted rounded-lg">
            <div className="flex items-start gap-2">
              <TrendingUp className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <p className="font-medium">Save more with larger packages</p>
                <p className="text-sm text-muted-foreground">
                  Enterprise packages offer up to 30% savings per credit compared to smaller packages.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Payment Methods */}
      <PaymentMethods
        paymentMethods={paymentMethods}
        onAdd={handleAddPaymentMethod}
        onDelete={handleDeletePaymentMethod}
        onSetDefault={handleSetDefaultPaymentMethod}
      />

      {/* Invoice History */}
      <Card>
        <CardHeader>
          <CardTitle>Invoice History</CardTitle>
          <CardDescription>
            Your billing history and downloadable invoices
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
          console.log('Credits added successfully')
        }}
      />
    </div>
  )
}
