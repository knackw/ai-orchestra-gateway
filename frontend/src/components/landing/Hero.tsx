'use client'

import * as React from 'react'
import Link from 'next/link'
import { ArrowRight, Play, Shield, Server, Zap } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const trustBadges = [
  { icon: Shield, label: 'DSGVO-konform' },
  { icon: Server, label: 'EU Hosting' },
  { icon: Zap, label: '99.9% Uptime' },
]

export function Hero() {
  const [isVisible, setIsVisible] = React.useState(false)

  React.useEffect(() => {
    setIsVisible(true)
  }, [])

  return (
    <section className="relative overflow-hidden">
      {/* Animated gradient background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-secondary/10" />
        <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]" />
      </div>

      <div className="container relative">
        <div className="mx-auto flex max-w-5xl flex-col items-center py-20 text-center md:py-32">
          {/* Main content with fade-in animation */}
          <div
            className={cn(
              'transition-all duration-1000',
              isVisible
                ? 'translate-y-0 opacity-100'
                : 'translate-y-10 opacity-0'
            )}
          >
            {/* Badge */}
            <div className="mb-8 inline-flex items-center rounded-full border bg-background/50 px-3 py-1 text-sm backdrop-blur-sm">
              <span className="mr-2 flex h-2 w-2">
                <span className="absolute inline-flex h-2 w-2 animate-ping rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500"></span>
              </span>
              v2.0 jetzt verfügbar
            </div>

            {/* Headline */}
            <h1 className="mb-6 bg-gradient-to-br from-foreground to-foreground/70 bg-clip-text text-4xl font-bold tracking-tight text-transparent sm:text-5xl md:text-6xl lg:text-7xl">
              AI Gateway mit
              <br />
              Datenschutz-Garantie
            </h1>

            {/* Subheadline */}
            <p className="mb-10 max-w-2xl text-lg text-muted-foreground md:text-xl">
              Multi-Tenant AI-Proxy mit automatischer PII-Erkennung.
              <br className="hidden sm:inline" />
              DSGVO-konform. Made in EU.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button size="lg" asChild className="group">
                <Link href="/signup">
                  Kostenlos starten
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link href="#features">
                  <Play className="mr-2 h-4 w-4" />
                  Live Demo
                </Link>
              </Button>
            </div>

            {/* Trust badges */}
            <div className="mt-16 flex flex-wrap items-center justify-center gap-8">
              {trustBadges.map((badge, index) => {
                const Icon = badge.icon
                return (
                  <div
                    key={badge.label}
                    className={cn(
                      'flex items-center gap-2 text-sm text-muted-foreground transition-all duration-500',
                      isVisible
                        ? 'translate-y-0 opacity-100'
                        : 'translate-y-10 opacity-0'
                    )}
                    style={{ transitionDelay: `${(index + 1) * 100}ms` }}
                  >
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                      <Icon className="h-4 w-4 text-primary" />
                    </div>
                    <span className="font-medium">{badge.label}</span>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
