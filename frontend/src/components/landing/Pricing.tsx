'use client'

import * as React from 'react'
import Link from 'next/link'
import { Check, Sparkles } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'

const pricingTiers = [
  {
    name: 'Starter',
    description: 'Perfekt für kleine Projekte und Tests',
    price: { monthly: 0, yearly: 0 },
    features: [
      '100 Credits/Monat',
      '1 API Key',
      'Community Support',
      'Basic Analytics',
      'PII Shield Basic',
      'EU Server',
    ],
    cta: 'Kostenlos starten',
    ctaVariant: 'outline' as const,
    href: '/signup',
  },
  {
    name: 'Professional',
    description: 'Für professionelle Anwendungen',
    price: { monthly: 49, yearly: 470 }, // 20% discount
    features: [
      '10.000 Credits/Monat',
      '10 API Keys',
      'Priority Support',
      'Advanced Analytics',
      'PII Shield Pro',
      'Provider Failover',
      'Custom Webhooks',
      'Audit Logs',
    ],
    cta: 'Jetzt upgraden',
    ctaVariant: 'default' as const,
    href: '/signup?plan=professional',
    highlighted: true,
    badge: 'Empfohlen',
  },
  {
    name: 'Enterprise',
    description: 'Maximale Kontrolle und Support',
    price: { monthly: null, yearly: null },
    customPrice: 'Auf Anfrage',
    features: [
      'Unlimited Credits',
      'Unlimited API Keys',
      'Dedicated Support',
      'Custom Integration',
      'SLA 99.9%',
      'On-Premise Option',
      'Dedicated Infrastructure',
      'Custom Training',
      'Legal Review',
    ],
    cta: 'Kontakt aufnehmen',
    ctaVariant: 'outline' as const,
    href: '/contact?plan=enterprise',
  },
]

export function Pricing() {
  const [isYearly, setIsYearly] = React.useState(false)

  return (
    <section id="pricing" className="py-20 md:py-32">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            Transparente Preise
          </h2>
          <p className="mb-8 text-lg text-muted-foreground">
            Wählen Sie den Plan, der zu Ihren Anforderungen passt.
            Keine versteckten Kosten.
          </p>

          {/* Monthly/Yearly Toggle */}
          <div className="mb-12 flex items-center justify-center gap-4">
            <Label htmlFor="billing-toggle" className={cn(!isYearly && 'font-semibold')}>
              Monatlich
            </Label>
            <Switch
              id="billing-toggle"
              checked={isYearly}
              onCheckedChange={setIsYearly}
            />
            <Label htmlFor="billing-toggle" className={cn(isYearly && 'font-semibold')}>
              Jährlich
            </Label>
            <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
              20% sparen
            </span>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid gap-8 lg:grid-cols-3">
          {pricingTiers.map((tier, index) => (
            <Card
              key={tier.name}
              className={cn(
                'relative flex flex-col transition-all duration-300 hover:shadow-lg',
                tier.highlighted && 'border-primary shadow-lg ring-2 ring-primary/20',
                'animate-in fade-in-50 slide-in-from-bottom-10'
              )}
              style={{
                animationDelay: `${index * 100}ms`,
                animationFillMode: 'backwards',
              }}
            >
              {tier.badge && (
                <div className="absolute -top-4 left-0 right-0 flex justify-center">
                  <span className="flex items-center gap-1 rounded-full bg-primary px-3 py-1 text-xs font-semibold text-primary-foreground">
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
                          €{isYearly ? tier.price.yearly : tier.price.monthly}
                        </span>
                        {tier.price.monthly !== 0 && (
                          <span className="text-muted-foreground">
                            /{isYearly ? 'Jahr' : 'Monat'}
                          </span>
                        )}
                      </div>
                      {isYearly && tier.price.monthly !== 0 && tier.price.yearly && (
                        <div className="mt-1 text-sm text-muted-foreground">
                          €{(tier.price.yearly / 12).toFixed(2)}/Monat
                        </div>
                      )}
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
                  className="w-full"
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
        <div className="mt-12 text-center text-sm text-muted-foreground">
          <p>
            Alle Preise zzgl. MwSt. Credits verfallen nicht.
            <br />
            Jederzeit kündbar. Keine Mindestlaufzeit.
          </p>
        </div>
      </div>
    </section>
  )
}
