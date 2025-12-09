'use client'

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Card } from '@/components/ui/card'
import { Loader2 } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface AddCreditsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

const creditPackages = [
  { id: '1000', credits: 1000, price: 10, popular: false },
  { id: '5000', credits: 5000, price: 45, popular: true },
  { id: '10000', credits: 10000, price: 80, popular: false },
  { id: '25000', credits: 25000, price: 180, popular: false },
]

export function AddCreditsDialog({
  open,
  onOpenChange,
  onSuccess,
}: AddCreditsDialogProps) {
  const [selectedPackage, setSelectedPackage] = useState(creditPackages[1].id)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handlePurchase = async () => {
    setLoading(true)
    try {
      // TODO: Integrate with Stripe Checkout
      // const response = await createCheckoutSession(selectedPackage)
      // window.location.href = response.url

      // Mock implementation
      await new Promise((resolve) => setTimeout(resolve, 1500))

      toast({
        title: 'Success',
        description: 'Credits added to your account',
      })

      if (onSuccess) {
        onSuccess()
      }

      onOpenChange(false)
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to process payment',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const selectedPkg = creditPackages.find((pkg) => pkg.id === selectedPackage)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Add Credits</DialogTitle>
          <DialogDescription>
            Choose a credit package to add to your account
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <RadioGroup value={selectedPackage} onValueChange={setSelectedPackage}>
            <div className="space-y-3">
              {creditPackages.map((pkg) => (
                <label key={pkg.id} htmlFor={pkg.id} className="cursor-pointer">
                  <Card
                    className={`p-4 transition-all ${
                      selectedPackage === pkg.id
                        ? 'border-primary ring-2 ring-primary'
                        : 'hover:border-primary/50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <RadioGroupItem value={pkg.id} id={pkg.id} />
                        <div>
                          <div className="flex items-center gap-2">
                            <Label htmlFor={pkg.id} className="font-semibold cursor-pointer">
                              {pkg.credits.toLocaleString()} Credits
                            </Label>
                            {pkg.popular && (
                              <span className="text-xs bg-primary text-primary-foreground px-2 py-0.5 rounded-full">
                                Popular
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground">
                            ${(pkg.price / pkg.credits * 1000).toFixed(2)} per 1K credits
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-lg">${pkg.price}</div>
                      </div>
                    </div>
                  </Card>
                </label>
              ))}
            </div>
          </RadioGroup>
        </div>

        {selectedPkg && (
          <div className="bg-muted p-4 rounded-lg space-y-2">
            <div className="flex justify-between text-sm">
              <span>Credits:</span>
              <span className="font-medium">
                {selectedPkg.credits.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Price:</span>
              <span className="font-medium">${selectedPkg.price}</span>
            </div>
            <div className="flex justify-between font-semibold pt-2 border-t">
              <span>Total:</span>
              <span>${selectedPkg.price}</span>
            </div>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handlePurchase} disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {loading ? 'Processing...' : 'Continue to Payment'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
