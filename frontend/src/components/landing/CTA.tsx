'use client'

import * as React from 'react'
import Link from 'next/link'
import { ArrowRight, Mail } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export function CTA() {
  const [email, setEmail] = React.useState('')
  const [isSubmitting, setIsSubmitting] = React.useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    // In a real implementation, you would send this to your backend
    // For now, we'll just redirect to signup with the email pre-filled
    window.location.href = `/signup?email=${encodeURIComponent(email)}`
  }

  return (
    <section className="relative overflow-hidden py-20 md:py-32">
      {/* Background gradient */}
      <div className="absolute inset-0 -z-10 bg-gradient-to-br from-primary/20 via-primary/10 to-background" />
      <div className="absolute inset-0 -z-10 bg-[url('/grid.svg')] bg-center opacity-50 [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]" />

      <div className="container">
        <div className="mx-auto max-w-3xl text-center">
          {/* Badge */}
          <div className="mb-6 inline-flex items-center rounded-full border bg-background/50 px-3 py-1 text-sm backdrop-blur-sm">
            <span className="mr-2 flex h-2 w-2">
              <span className="absolute inline-flex h-2 w-2 animate-ping rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500"></span>
            </span>
            100% kostenlos starten
          </div>

          {/* Headline */}
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            Bereit für sichere KI-Integration?
          </h2>

          {/* Subheadline */}
          <p className="mb-10 text-lg text-muted-foreground md:text-xl">
            Starten Sie in weniger als 5 Minuten.
            <br className="hidden sm:inline" />
            Keine Kreditkarte erforderlich.
          </p>

          {/* Email form */}
          <form
            onSubmit={handleSubmit}
            className="mx-auto mb-6 flex max-w-md flex-col gap-3 sm:flex-row"
          >
            <div className="relative flex-1">
              <Mail className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
              <Input
                type="email"
                placeholder="ihre.email@firma.de"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="h-12 pl-10"
              />
            </div>
            <Button
              type="submit"
              size="lg"
              className="group h-12"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                'Wird geladen...'
              ) : (
                <>
                  Kostenlos starten
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </>
              )}
            </Button>
          </form>

          {/* Or divider */}
          <div className="mb-6 flex items-center gap-4">
            <div className="h-px flex-1 bg-border" />
            <span className="text-sm text-muted-foreground">oder</span>
            <div className="h-px flex-1 bg-border" />
          </div>

          {/* Direct signup link */}
          <Button variant="outline" size="lg" asChild>
            <Link href="/signup">Direkt zur Registrierung</Link>
          </Button>

          {/* Trust indicators */}
          <div className="mt-10 flex flex-wrap items-center justify-center gap-6 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <svg
                className="h-5 w-5 text-green-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <span>Keine Kreditkarte</span>
            </div>
            <div className="flex items-center gap-2">
              <svg
                className="h-5 w-5 text-green-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <span>100 Credits gratis</span>
            </div>
            <div className="flex items-center gap-2">
              <svg
                className="h-5 w-5 text-green-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <span>Jederzeit kündbar</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
