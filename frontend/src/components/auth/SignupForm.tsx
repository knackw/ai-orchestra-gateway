'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Eye, EyeOff, Loader2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { useToast } from '@/hooks/use-toast'
import { signupSchema, type SignupInput } from '@/lib/validations/auth'
import { signUp } from '@/lib/auth'
import { MathCaptcha, Honeypot } from '@/components/security'
import { PasswordStrengthIndicator } from './PasswordStrengthIndicator'

export function SignupForm() {
  const router = useRouter()
  const { toast } = useToast()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isCaptchaValid, setIsCaptchaValid] = useState(false)
  const honeypotRef = useRef<HTMLInputElement>(null)

  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors },
  } = useForm<SignupInput>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      acceptTerms: false,
      acceptPrivacy: false,
      acceptAvv: false,
    },
  })

  const password = watch('password', '')

  const onSubmit = async (data: SignupInput) => {
    // SEC-004: Check honeypot - if filled, silently reject (bot detected)
    if (honeypotRef.current?.value) {
      // Simulate success to confuse bots
      await new Promise(resolve => setTimeout(resolve, 1000))
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
      await signUp(data.email, data.password, {
        company: data.company,
      })

      toast({
        title: 'Registrierung erfolgreich',
        description: 'Bitte überprüfen Sie Ihre E-Mails zur Bestätigung.',
      })

      router.push(`/verify-email?email=${encodeURIComponent(data.email)}`)
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Registrierung fehlgeschlagen',
        description:
          error instanceof Error
            ? error.message
            : 'Ein Fehler ist aufgetreten.',
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* SEC-004: Honeypot field for bot detection */}
      <Honeypot ref={honeypotRef} name="company_url" />

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

      <div className="space-y-2">
        <Label htmlFor="password">Passwort</Label>
        <div className="relative">
          <Input
            id="password"
            type={showPassword ? 'text' : 'password'}
            placeholder="Mindestens 12 Zeichen, 1 Großbuchstabe, 1 Zahl, 1 Sonderzeichen"
            autoComplete="new-password"
            {...register('password')}
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            disabled={isLoading}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
        {errors.password && (
          <p className="text-sm text-destructive">{errors.password.message}</p>
        )}
        {password && <PasswordStrengthIndicator password={password} className="mt-2" />}
      </div>

      <div className="space-y-2">
        <Label htmlFor="confirmPassword">Passwort bestätigen</Label>
        <div className="relative">
          <Input
            id="confirmPassword"
            type={showConfirmPassword ? 'text' : 'password'}
            placeholder="••••••••"
            autoComplete="new-password"
            {...register('confirmPassword')}
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            disabled={isLoading}
          >
            {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
        {errors.confirmPassword && (
          <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="company">Firmenname (optional)</Label>
        <Input
          id="company"
          type="text"
          placeholder="Ihr Firmenname"
          autoComplete="organization"
          {...register('company')}
          disabled={isLoading}
        />
        {errors.company && (
          <p className="text-sm text-destructive">{errors.company.message}</p>
        )}
      </div>

      <div className="space-y-3 pt-2">
        <div className="flex items-start space-x-2">
          <Controller
            name="acceptTerms"
            control={control}
            render={({ field }) => (
              <Checkbox
                id="acceptTerms"
                checked={field.value}
                onCheckedChange={field.onChange}
                className="mt-1"
                disabled={isLoading}
              />
            )}
          />
          <Label htmlFor="acceptTerms" className="text-sm font-normal">
            Ich akzeptiere die{' '}
            <Link href="/terms" className="text-primary hover:underline" target="_blank">
              AGB
            </Link>
          </Label>
        </div>
        {errors.acceptTerms && (
          <p className="text-sm text-destructive">{errors.acceptTerms.message}</p>
        )}

        <div className="flex items-start space-x-2">
          <Controller
            name="acceptPrivacy"
            control={control}
            render={({ field }) => (
              <Checkbox
                id="acceptPrivacy"
                checked={field.value}
                onCheckedChange={field.onChange}
                className="mt-1"
                disabled={isLoading}
              />
            )}
          />
          <Label htmlFor="acceptPrivacy" className="text-sm font-normal">
            Ich akzeptiere die{' '}
            <Link href="/privacy" className="text-primary hover:underline" target="_blank">
              Datenschutzerklärung
            </Link>
          </Label>
        </div>
        {errors.acceptPrivacy && (
          <p className="text-sm text-destructive">{errors.acceptPrivacy.message}</p>
        )}

        <div className="flex items-start space-x-2">
          <Controller
            name="acceptAvv"
            control={control}
            render={({ field }) => (
              <Checkbox
                id="acceptAvv"
                checked={field.value}
                onCheckedChange={field.onChange}
                className="mt-1"
                disabled={isLoading}
              />
            )}
          />
          <Label htmlFor="acceptAvv" className="text-sm font-normal">
            Ich akzeptiere den{' '}
            <Link href="/avv" className="text-primary hover:underline" target="_blank">
              Auftragsverarbeitungsvertrag (AVV)
            </Link>
          </Label>
        </div>
        {errors.acceptAvv && (
          <p className="text-sm text-destructive">{errors.acceptAvv.message}</p>
        )}
      </div>

      {/* SEC-004: Math CAPTCHA for bot protection */}
      <MathCaptcha
        onVerify={setIsCaptchaValid}
        disabled={isLoading}
      />

      <Button type="submit" className="w-full" disabled={isLoading || !isCaptchaValid}>
        {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {isLoading ? 'Wird registriert...' : 'Registrieren'}
      </Button>

      <div className="text-center text-sm text-slate-600">
        Bereits ein Konto?{' '}
        <Link href="/login" className="font-semibold text-primary hover:underline">
          Jetzt anmelden
        </Link>
      </div>
    </form>
  )
}
