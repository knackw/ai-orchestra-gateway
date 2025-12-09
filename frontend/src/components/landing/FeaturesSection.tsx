'use client'

import * as React from 'react'
import {
  Shield,
  Network,
  MapPin,
  BarChart3,
  Code2,
  Palette,
} from 'lucide-react'

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { cn } from '@/lib/utils'

const features = [
  {
    icon: Shield,
    title: 'Privacy Shield',
    description:
      'Automatische PII-Erkennung und Anonymisierung. Schützt E-Mail-Adressen, Telefonnummern, IBAN und weitere sensible Daten vor der Übertragung an AI-Provider.',
    color: 'bg-blue-500/10 text-blue-500',
  },
  {
    icon: Network,
    title: 'Multi-Provider',
    description:
      'Nahtlose Integration mit Anthropic, Scaleway und Vertex AI. Automatisches Failover bei Ausfällen. Wählen Sie den besten Provider für Ihren Use Case.',
    color: 'bg-purple-500/10 text-purple-500',
  },
  {
    icon: MapPin,
    title: 'EU-Hosting',
    description:
      '100% DSGVO-konform durch EU Data Residency. Alle Daten werden auf deutschen Servern gespeichert. Vollständige Compliance mit europäischen Datenschutzgesetzen.',
    color: 'bg-green-500/10 text-green-500',
  },
  {
    icon: BarChart3,
    title: 'Usage Tracking',
    description:
      'Transparente Abrechnung mit detaillierten Analytics. Echtzeit-Überwachung von API-Calls, Kosten und Performance. Volle Kostenkontrolle für Ihr Budget.',
    color: 'bg-orange-500/10 text-orange-500',
  },
  {
    icon: Code2,
    title: 'API-First',
    description:
      'RESTful API mit vollständiger OpenAPI-Dokumentation. SDK-kompatibel mit gängigen AI-Bibliotheken. Einfache Integration in Ihre bestehende Infrastruktur.',
    color: 'bg-pink-500/10 text-pink-500',
  },
  {
    icon: Palette,
    title: 'White-Label',
    description:
      'Vollständig anpassbar für SaaS-Anbieter. Eigenes Branding, Custom Domain und individuelles Billing. Perfekt für Reseller und Plattform-Betreiber.',
    color: 'bg-red-500/10 text-red-500',
  },
]

export function FeaturesSection() {
  return (
    <section id="features" className="py-20 md:py-32">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            Enterprise Features
          </h2>
          <p className="mb-16 text-lg text-muted-foreground">
            Alles, was Sie für sichere und skalierbare AI-Integration benötigen.
            Production-ready und sofort einsatzbereit.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card
                key={feature.title}
                className={cn(
                  'group relative overflow-hidden transition-all duration-300 hover:shadow-lg',
                  'animate-in fade-in-50 slide-in-from-bottom-10',
                )}
                style={{
                  animationDelay: `${index * 100}ms`,
                  animationFillMode: 'backwards',
                }}
              >
                <CardHeader>
                  <div
                    className={cn(
                      'mb-4 flex h-12 w-12 items-center justify-center rounded-lg transition-transform duration-300 group-hover:scale-110',
                      feature.color
                    )}
                  >
                    <Icon className="h-6 w-6" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardContent>

                {/* Hover effect gradient */}
                <div className="absolute inset-0 -z-10 bg-gradient-to-br from-primary/5 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
              </Card>
            )
          })}
        </div>

        {/* Additional info section */}
        <div className="mt-16 text-center">
          <p className="text-muted-foreground">
            Benötigen Sie weitere Features?{' '}
            <a
              href="/contact"
              className="font-medium text-primary hover:underline"
            >
              Sprechen Sie uns an
            </a>
          </p>
        </div>
      </div>
    </section>
  )
}
