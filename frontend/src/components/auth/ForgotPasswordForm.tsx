'use client'

import { useState, useRef } from 'react'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Loader2, ArrowLeft } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/use-toast'
import { forgotPasswordSchema, type ForgotPasswordInput } from '@/lib/validations/auth'
import { resetPassword } from '@/lib/auth'
import { MathCaptcha, Honeypot } from '@/components/security'

export function ForgotPasswordForm() {
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [isCaptchaValid, setIsCaptchaValid] = useState(false)
  const honeypotRef = useRef<HTMLInputElement>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordInput>({
    resolver: zodResolver(forgotPasswordSchema),
  })

  const onSubmit = async (data: ForgotPasswordInput) => {
    // SEC-004: Check honeypot - if filled, silently reject (bot detected)
    if (honeypotRef.current?.value) {
      // Simulate success to confuse bots
      await new Promise(resolve => setTimeout(resolve, 1000))
      setIsSubmitted(true)
      return
    }

    // SEC-004: Validate CAPTCHA
    if (!isCaptchaValid) {
      toast({
        variant: 'destructive',
        title: 'Sicherheitsfrage',
        description: 'Bitte losen Sie die Rechenaufgabe korrekt.',
      })
      return
    }

    setIsLoading(true)

    try {
      await resetPassword(data.email)
      setIsSubmitted(true)

      toast({
        title: 'E-Mail versendet',
        description: 'Bitte überprüfen Sie Ihr Postfach.',
      })
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Fehler',
        description:
          error instanceof Error
            ? error.message
            : 'Ein Fehler ist aufgetreten.',
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (isSubmitted) {
    return (
      <div className="space-y-6 text-center">
        <div className="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-medium">E-Mail gesendet</h3>
          <p className="text-sm text-muted-foreground mt-2">
            Falls ein Konto mit dieser E-Mail-Adresse existiert, erhalten Sie in Kuerze einen Link zum Zuruecksetzen Ihres Passworts.
          </p>
        </div>
        <Link href="/login">
          <Button variant="outline" className="w-full">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Zurueck zum Login
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* SEC-004: Honeypot field for bot detection */}
      <Honeypot ref={honeypotRef} name="phone" />

      <div className="space-y-2">
        <Label htmlFor="email">E-Mail</Label>
        <Input
          id="email"
          type="email"
          placeholder="ihre.email@beispiel.de"
          autoComplete="email"
          {...register('email')}
          disabled={isLoading}
        />
        {errors.email && (
          <p className="text-sm text-destructive">{errors.email.message}</p>
        )}
      </div>

      {/* SEC-004: Math CAPTCHA for bot protection */}
      <MathCaptcha
        onVerify={setIsCaptchaValid}
        disabled={isLoading}
      />

      <Button type="submit" className="w-full" disabled={isLoading || !isCaptchaValid}>
        {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        Link senden
      </Button>

      <div className="text-center">
        <Link href="/login" className="text-sm text-primary hover:underline">
          <ArrowLeft className="inline-block mr-1 h-4 w-4" />
          Zurueck zum Login
        </Link>
      </div>
    </form>
  )
}
