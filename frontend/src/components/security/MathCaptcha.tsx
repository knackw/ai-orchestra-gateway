'use client'

import { useState, useEffect, useCallback } from 'react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'

/**
 * SEC-004: Math CAPTCHA Component
 *
 * A simple, DSGVO-compliant CAPTCHA that doesn't require external services.
 * Uses basic math questions to verify human users.
 *
 * @example
 * ```tsx
 * <MathCaptcha
 *   onVerify={(isValid) => setIsCaptchaValid(isValid)}
 *   label="Sicherheitsfrage"
 * />
 * ```
 */
interface MathCaptchaProps {
  onVerify: (isValid: boolean) => void
  label?: string
  disabled?: boolean
  className?: string
}

type Operation = '+' | '-' | '*'

function generateQuestion(): { num1: number; num2: number; operation: Operation; answer: number } {
  // Use different operations for variety
  const operations: Operation[] = ['+', '-', '*']
  const operation = operations[Math.floor(Math.random() * operations.length)]

  let num1: number
  let num2: number
  let answer: number

  switch (operation) {
    case '+':
      num1 = Math.floor(Math.random() * 10) + 1 // 1-10
      num2 = Math.floor(Math.random() * 10) + 1 // 1-10
      answer = num1 + num2
      break
    case '-':
      num1 = Math.floor(Math.random() * 10) + 5 // 5-14 (ensure positive result)
      num2 = Math.floor(Math.random() * num1) + 1 // 1 to num1
      answer = num1 - num2
      break
    case '*':
      num1 = Math.floor(Math.random() * 5) + 1 // 1-5
      num2 = Math.floor(Math.random() * 5) + 1 // 1-5
      answer = num1 * num2
      break
  }

  return { num1, num2, operation, answer }
}

function getOperationSymbol(operation: Operation): string {
  switch (operation) {
    case '+': return '+'
    case '-': return '-'
    case '*': return 'x'
  }
}

export function MathCaptcha({
  onVerify,
  label = 'Sicherheitsfrage',
  disabled = false,
  className = ''
}: MathCaptchaProps) {
  const [question, setQuestion] = useState(() => generateQuestion())
  const [userAnswer, setUserAnswer] = useState('')
  const [hasAttempted, setHasAttempted] = useState(false)

  const regenerateQuestion = useCallback(() => {
    setQuestion(generateQuestion())
    setUserAnswer('')
    setHasAttempted(false)
    onVerify(false)
  }, [onVerify])

  useEffect(() => {
    // Generate new question on mount
    regenerateQuestion()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setUserAnswer(value)
    setHasAttempted(true)

    // Only verify if user has entered something
    if (value.trim() !== '') {
      const isCorrect = parseInt(value, 10) === question.answer
      onVerify(isCorrect)
    } else {
      onVerify(false)
    }
  }

  const isCorrect = hasAttempted && parseInt(userAnswer, 10) === question.answer
  const isIncorrect = hasAttempted && userAnswer.trim() !== '' && parseInt(userAnswer, 10) !== question.answer

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center justify-between">
        <Label htmlFor="captcha-answer">{label}</Label>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={regenerateQuestion}
          disabled={disabled}
          className="h-8 px-2 text-muted-foreground hover:text-foreground"
          title="Neue Aufgabe"
        >
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-lg font-mono bg-muted px-3 py-2 rounded-md select-none">
          <span>{question.num1}</span>
          <span>{getOperationSymbol(question.operation)}</span>
          <span>{question.num2}</span>
          <span>=</span>
        </div>
        <Input
          id="captcha-answer"
          type="number"
          inputMode="numeric"
          pattern="[0-9]*"
          value={userAnswer}
          onChange={handleChange}
          className={`w-20 text-center ${
            isCorrect ? 'border-green-500 focus-visible:ring-green-500' : ''
          } ${
            isIncorrect ? 'border-destructive focus-visible:ring-destructive' : ''
          }`}
          disabled={disabled}
          required
          aria-describedby="captcha-hint"
          autoComplete="off"
        />
      </div>
      <p id="captcha-hint" className="text-xs text-muted-foreground">
        Bitte losen Sie die Rechenaufgabe, um fortzufahren.
      </p>
      {isIncorrect && (
        <p className="text-sm text-destructive">
          Falsche Antwort. Bitte versuchen Sie es erneut.
        </p>
      )}
    </div>
  )
}
