'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  CreditCard as CreditCardIcon,
  Plus,
  Trash2,
  CheckCircle2,
} from 'lucide-react'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { useState } from 'react'
import { useToast } from '@/hooks/use-toast'

export type PaymentMethod = {
  id: string
  type: 'card'
  brand: string
  last4: string
  expiryMonth: number
  expiryYear: number
  isDefault: boolean
}

interface PaymentMethodsProps {
  paymentMethods: PaymentMethod[]
  onAdd: () => void
  onDelete: (id: string) => void
  onSetDefault: (id: string) => void
}

export function PaymentMethods({
  paymentMethods,
  onAdd,
  onDelete,
  onSetDefault,
}: PaymentMethodsProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [selectedMethod, setSelectedMethod] = useState<PaymentMethod | null>(null)
  const { toast } = useToast()

  const confirmDelete = (method: PaymentMethod) => {
    setSelectedMethod(method)
    setDeleteDialogOpen(true)
  }

  const handleDelete = () => {
    if (selectedMethod) {
      onDelete(selectedMethod.id)
      toast({
        title: 'Payment Method Removed',
        description: 'The payment method has been removed from your account.',
      })
    }
    setDeleteDialogOpen(false)
    setSelectedMethod(null)
  }

  const getCardBrandIcon = () => {
    // In a real app, you'd return actual brand logos
    return <CreditCardIcon className="h-6 w-6" />
  }

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Payment Methods</CardTitle>
              <CardDescription>Manage your payment methods</CardDescription>
            </div>
            <Button onClick={onAdd} size="sm">
              <Plus className="mr-2 h-4 w-4" />
              Add Card
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {paymentMethods.length === 0 ? (
            <div className="text-center py-6">
              <CreditCardIcon className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground mb-4">
                No payment methods added yet
              </p>
              <Button onClick={onAdd} variant="outline">
                <Plus className="mr-2 h-4 w-4" />
                Add Payment Method
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {paymentMethods.map((method) => (
                <div
                  key={method.id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    {getCardBrandIcon()}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium capitalize">
                          {method.brand}
                        </span>
                        <span className="text-muted-foreground">
                          •••• {method.last4}
                        </span>
                        {method.isDefault && (
                          <Badge variant="secondary" className="text-xs">
                            Default
                          </Badge>
                        )}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Expires {method.expiryMonth.toString().padStart(2, '0')}/
                        {method.expiryYear}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {!method.isDefault && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onSetDefault(method.id)}
                      >
                        <CheckCircle2 className="mr-2 h-4 w-4" />
                        Set as Default
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => confirmDelete(method)}
                      disabled={method.isDefault && paymentMethods.length === 1}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove Payment Method?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to remove this payment method? This action
              cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-destructive">
              Remove
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
