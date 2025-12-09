'use client'

import { useMemo } from 'react'
import { getPasswordStrength } from '@/lib/validations/auth'

interface PasswordStrengthIndicatorProps {
  password: string
  className?: string
}

export function PasswordStrengthIndicator({
  password,
  className = '',
}: PasswordStrengthIndicatorProps) {
  const strength = useMemo(() => {
    if (!password) return null
    return getPasswordStrength(password)
  }, [password])

  if (!strength) return null

  const getBarColor = (index: number) => {
    if (strength.score <= 3) {
      return index < 2 ? 'bg-red-500' : 'bg-gray-200'
    } else if (strength.score <= 5) {
      return index < 3 ? 'bg-yellow-500' : 'bg-gray-200'
    } else if (strength.score <= 7) {
      return index < 4 ? 'bg-green-500' : 'bg-gray-200'
    } else {
      return 'bg-green-600'
    }
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Strength bars */}
      <div className="flex gap-1">
        {[0, 1, 2, 3].map((index) => (
          <div
            key={index}
            className={`h-1 flex-1 rounded-full transition-colors duration-300 ${getBarColor(index)}`}
          />
        ))}
      </div>

      {/* Strength label */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">Passwortstärke:</span>
        <span className={`font-medium ${strength.color}`}>
          {strength.label}
        </span>
      </div>

      {/* Requirements checklist */}
      <div className="space-y-1 text-xs text-muted-foreground">
        <div className={password.length >= 12 ? 'text-green-600' : ''}>
          {password.length >= 12 ? '✓' : '○'} Mindestens 12 Zeichen
        </div>
        <div className={/[A-Z]/.test(password) ? 'text-green-600' : ''}>
          {/[A-Z]/.test(password) ? '✓' : '○'} Einen Großbuchstaben
        </div>
        <div className={/[a-z]/.test(password) ? 'text-green-600' : ''}>
          {/[a-z]/.test(password) ? '✓' : '○'} Einen Kleinbuchstaben
        </div>
        <div className={/[0-9]/.test(password) ? 'text-green-600' : ''}>
          {/[0-9]/.test(password) ? '✓' : '○'} Eine Zahl
        </div>
        <div className={/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password) ? 'text-green-600' : ''}>
          {/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password) ? '✓' : '○'} Ein Sonderzeichen
        </div>
      </div>
    </div>
  )
}
