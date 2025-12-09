'use client'

import * as React from 'react'
import {
  Shield,
  Building2,
  CreditCard,
  RefreshCw,
  BarChart3,
  Flag,
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
    title: 'PII Shield',
    description:
      'Automatische Erkennung & Redaktion personenbezogener Daten (E-Mail, Telefon, IBAN) vor dem Versand an AI-Provider.',
    color: 'bg-blue-500/10 text-blue-500',
  },
  {
    icon: Building2,
    title: 'Multi-Tenant',
    description:
      'Isolierte Mandanten mit eigenen Credits, API-Keys und vollständiger Datentrennung durch Row-Level Security.',
    color: 'bg-purple-500/10 text-purple-500',
  },
  {
    icon: CreditCard,
    title: 'Pay-per-Use',
    description:
      'Flexible Credit-basierte Abrechnung ohne Grundgebühr. Nur zahlen, was Sie wirklich nutzen. Volle Kostenkontrolle.',
    color: 'bg-green-500/10 text-green-500',
  },
  {
    icon: RefreshCw,
    title: 'Provider Failover',
    description:
      'Automatischer Wechsel zwischen AI-Providern (Anthropic, Scaleway) bei Ausfall oder Rate Limits. 99.9% Verfügbarkeit.',
    color: 'bg-orange-500/10 text-orange-500',
  },
  {
    icon: BarChart3,
    title: 'Usage Analytics',
    description:
      'Detaillierte Nutzungsstatistiken in Echtzeit. Überwachen Sie Kosten, API-Calls und Performance pro Mandant.',
    color: 'bg-pink-500/10 text-pink-500',
  },
  {
    icon: Flag,
    title: 'DSGVO-konform',
    description:
      'EU Data Residency, deutsche Server, vollständige DSGVO-Compliance. Audit-Logs für alle Datenzugriffe.',
    color: 'bg-red-500/10 text-red-500',
  },
]

export function Features() {
  return (
    <section id="features" className="py-20 md:py-32">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            Enterprise-Grade AI Gateway
          </h2>
          <p className="mb-16 text-lg text-muted-foreground">
            Alle Features, die Sie für sichere AI-Integration benötigen.
            Production-ready und skalierbar.
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
      </div>
    </section>
  )
}
