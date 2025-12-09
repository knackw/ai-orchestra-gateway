'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Check } from 'lucide-react'

interface PlanCardProps {
  planName: string
  planType: 'free' | 'pro' | 'enterprise'
  features: string[]
  onUpgrade?: () => void
}

export function PlanCard({ planName, planType, features, onUpgrade }: PlanCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Current Plan</CardTitle>
            <CardDescription>Your subscription details</CardDescription>
          </div>
          <Badge variant={planType === 'free' ? 'secondary' : 'default'} className="text-sm">
            {planName}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <p className="text-sm font-medium">Plan Features:</p>
          <ul className="space-y-2">
            {features.map((feature, index) => (
              <li key={index} className="flex items-start gap-2 text-sm">
                <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                <span>{feature}</span>
              </li>
            ))}
          </ul>
        </div>

        {planType !== 'enterprise' && onUpgrade && (
          <Button onClick={onUpgrade} className="w-full">
            Upgrade Plan
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
