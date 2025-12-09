'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { Loader2, CheckCircle, Mail } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'
import { resendVerificationEmail } from '@/lib/auth'

export function VerifyEmailCard() {
  const searchParams = useSearchParams()
  const { toast } = useToast()
  const [isResending, setIsResending] = useState(false)
  const email = searchParams.get('email') || ''

  const handleResendEmail = async () => {
    if (!email) {
      toast({
        variant: 'destructive',
        title: 'Fehler',
        description: 'E-Mail-Adresse nicht gefunden.',
      })
      return
    }

    setIsResending(true)

    try {
      await resendVerificationEmail(email)

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
      setIsResending(false)
    }
  }

  return (
    <div className="space-y-6 text-center">
      <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
        <Mail className="w-8 h-8 text-blue-600" />
      </div>

      <div className="space-y-2">
        <h3 className="text-2xl font-bold">E-Mail bestätigen</h3>
        <p className="text-sm text-muted-foreground">
          Wir haben Ihnen eine E-Mail mit einem Bestätigungslink gesendet.
        </p>
        {email && (
          <p className="text-sm font-medium text-slate-900">{email}</p>
        )}
      </div>

      <div className="space-y-3 pt-4">
        <p className="text-sm text-muted-foreground">
          Keine E-Mail erhalten?
        </p>

        <Button
          onClick={handleResendEmail}
          variant="outline"
          className="w-full"
          disabled={isResending}
        >
          {isResending ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Wird versendet...
            </>
          ) : (
            'E-Mail erneut senden'
          )}
        </Button>

        <div className="pt-4">
          <Link href="/login">
            <Button variant="link" className="text-sm">
              Zurück zum Login
            </Button>
          </Link>
        </div>
      </div>

      <div className="text-xs text-muted-foreground pt-4">
        <p>Überprüfen Sie auch Ihren Spam-Ordner.</p>
      </div>
    </div>
  )
}
