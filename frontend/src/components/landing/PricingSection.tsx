'use client'

import * as React from 'react'
import Link from 'next/link'
import { Check, Sparkles, Zap } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { cn } from '@/lib/utils'

const pricingTiers = [
  {
    name: 'Starter',
    description: 'Perfekt für kleine Projekte und Tests',
    price: 49,
    priceMonthly: '49',
    credits: '100k',
    features: [
      '100.000 Tokens/Monat',
      'Privacy Shield Basic',
      'Multi-Provider Support',
      '2 API Keys',
      'Community Support',
      'Basic Analytics',
      'EU Server Hosting',
    ],
    cta: 'Jetzt starten',
    ctaVariant: 'outline' as const,
    href: '/signup?plan=starter',
  },
  {
    name: 'Professional',
    description: 'Für professionelle Anwendungen',
    price: 199,
    priceMonthly: '199',
    credits: '500k',
    features: [
      '500.000 Tokens/Monat',
      'Privacy Shield Pro',
      'Multi-Provider Failover',
      '10 API Keys',
      'Priority Support (24h)',
      'Advanced Analytics',
      'Custom Webhooks',
      'Audit Logs & Compliance',
      'SLA 99.9% Uptime',
    ],
    cta: 'Professional wählen',
    ctaVariant: 'default' as const,
    href: '/signup?plan=professional',
    highlighted: true,
    badge: 'Beliebt',
  },
  {
    name: 'Enterprise',
    description: 'Maximale Kontrolle und Support',
    price: null,
    customPrice: 'Auf Anfrage',
    credits: 'Unlimited',
    features: [
      'Unlimited Tokens',
      'Privacy Shield Enterprise',
      'Dedicated Infrastructure',
      'Unlimited API Keys',
      '24/7 Premium Support',
      'Custom Integration',
      'On-Premise Option',
      'SLA 99.95% Uptime',
      'Legal Review & AVV',
      'Custom Training',
      'White-Label Lösung',
    ],
    cta: 'Kontakt aufnehmen',
    ctaVariant: 'outline' as const,
    href: '/contact?plan=enterprise',
  },
]

export function PricingSection() {
  return (
    <section id="pricing" className="py-20 md:py-32">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            Transparente Preise
          </h2>
          <p className="mb-12 text-lg text-muted-foreground">
            Wählen Sie den Plan, der zu Ihren Anforderungen passt.
            <br />
            Keine versteckten Kosten. Jederzeit kündbar.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid gap-8 lg:grid-cols-3">
          {pricingTiers.map((tier, index) => (
            <Card
              key={tier.name}
              className={cn(
                'relative flex flex-col transition-all duration-300 hover:shadow-xl',
                tier.highlighted && 'border-primary shadow-xl ring-2 ring-primary/20 scale-105',
                'animate-in fade-in-50 slide-in-from-bottom-10'
              )}
              style={{
                animationDelay: `${index * 100}ms`,
                animationFillMode: 'backwards',
              }}
            >
              {tier.badge && (
                <div className="absolute -top-4 left-0 right-0 flex justify-center">
                  <span className="flex items-center gap-1 rounded-full bg-primary px-3 py-1 text-xs font-semibold text-primary-foreground shadow-lg">
                    <Sparkles className="h-3 w-3" />
                    {tier.badge}
                  </span>
                </div>
              )}

              <CardHeader className={cn(tier.highlighted && 'pt-8')}>
                <CardTitle className="text-2xl">{tier.name}</CardTitle>
                <CardDescription>{tier.description}</CardDescription>
              </CardHeader>

              <CardContent className="flex-1">
                {/* Price */}
                <div className="mb-6">
                  {tier.customPrice ? (
                    <div className="text-3xl font-bold">{tier.customPrice}</div>
                  ) : (
                    <>
                      <div className="flex items-baseline gap-1">
                        <span className="text-4xl font-bold">
                          €{tier.priceMonthly}
                        </span>
                        <span className="text-muted-foreground">/Monat</span>
                      </div>
                      <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
                        <Zap className="h-4 w-4 text-primary" />
                        {tier.credits} Tokens inkludiert
                      </div>
                    </>
                  )}
                </div>

                {/* Features */}
                <ul className="space-y-3">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3">
                      <Check className="mt-0.5 h-5 w-5 flex-shrink-0 text-primary" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>

              <CardFooter>
                <Button
                  variant={tier.ctaVariant}
                  className={cn(
                    'w-full',
                    tier.highlighted && 'shadow-lg'
                  )}
                  size="lg"
                  asChild
                >
                  <Link href={tier.href}>{tier.cta}</Link>
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>

        {/* Additional Info */}
        <div className="mt-16 text-center">
          <div className="mx-auto max-w-2xl rounded-lg border bg-muted/50 p-6">
            <p className="text-sm text-muted-foreground">
              Alle Preise zzgl. MwSt. Credits verfallen nicht und können jederzeit nachgekauft werden.
              <br />
              <strong>14 Tage Geld-zurück-Garantie.</strong> Keine Mindestlaufzeit.
            </p>
          </div>
        </div>

        {/* FAQ Link */}
        <div className="mt-8 text-center">
          <p className="text-muted-foreground">
            Fragen zur Preisgestaltung?{' '}
            <a
              href="#faq"
              className="font-medium text-primary hover:underline"
            >
              Schauen Sie in unsere FAQ
            </a>
          </p>
        </div>
      </div>
    </section>
  )
}
