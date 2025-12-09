'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Plus, TrendingDown } from 'lucide-react'

interface CreditBalanceProps {
  currentCredits: number
  monthlyAllocation?: number
  onAddCredits: () => void
}

export function CreditBalance({
  currentCredits,
  monthlyAllocation,
  onAddCredits,
}: CreditBalanceProps) {
  const percentageUsed = monthlyAllocation
    ? ((monthlyAllocation - currentCredits) / monthlyAllocation) * 100
    : 0

  return (
    <Card>
      <CardHeader>
        <CardTitle>Credit Balance</CardTitle>
        <CardDescription>Your available credits</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-baseline justify-between">
            <div>
              <div className="text-4xl font-bold">
                {currentCredits.toLocaleString()}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                credits remaining
              </p>
            </div>
            <TrendingDown className="h-8 w-8 text-muted-foreground" />
          </div>

          {monthlyAllocation && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Usage this month</span>
                <span className="font-medium">
                  {((monthlyAllocation - currentCredits) / monthlyAllocation * 100).toFixed(1)}%
                </span>
              </div>
              <Progress value={percentageUsed} className="h-2" />
              <p className="text-xs text-muted-foreground">
                {(monthlyAllocation - currentCredits).toLocaleString()} of{' '}
                {monthlyAllocation.toLocaleString()} credits used
              </p>
            </div>
          )}
        </div>

        <Button onClick={onAddCredits} className="w-full">
          <Plus className="mr-2 h-4 w-4" />
          Add Credits
        </Button>

        <div className="text-xs text-muted-foreground">
          Estimated to last ~15 days at current usage rate
        </div>
      </CardContent>
    </Card>
  )
}
