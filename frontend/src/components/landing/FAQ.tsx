'use client'

import * as React from 'react'

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'

const faqs = [
  {
    question: 'Was ist AI Legal Ops?',
    answer:
      'AI Legal Ops ist ein Enterprise-Grade AI Gateway, das als sicherer Proxy zwischen Ihrer Anwendung und verschiedenen AI-Providern (Anthropic, Scaleway) agiert. Wir bieten automatische PII-Erkennung, Multi-Tenant-Verwaltung, Credit-basierte Abrechnung und vollständige DSGVO-Compliance. Damit können Sie AI-Funktionen sicher in Ihre Anwendung integrieren, ohne sich um Datenschutz oder Provider-Management kümmern zu müssen.',
  },
  {
    question: 'Wie funktioniert der PII Shield?',
    answer:
      'Der PII Shield ist unser automatisches Datenschutz-System, das alle Anfragen vor dem Versand an AI-Provider scannt. Es erkennt und redaktiert personenbezogene Daten wie E-Mail-Adressen, Telefonnummern, IBAN, Namen und Adressen. Die erkannten Daten werden durch Platzhalter ersetzt, an den AI-Provider gesendet, und in der Antwort wieder eingefügt. So bleiben Ihre Daten DSGVO-konform geschützt, während die AI-Funktionalität erhalten bleibt.',
  },
  {
    question: 'Welche AI-Provider werden unterstützt?',
    answer:
      'Aktuell unterstützen wir Anthropic (Claude) und Scaleway AI mit mehreren Modellen (Claude Opus, Sonnet, Haiku, Llama 3.1). Unser System bietet automatisches Failover zwischen Providern: Wenn ein Provider ausfällt oder Rate Limits erreicht, wechseln wir automatisch zum nächsten verfügbaren Provider. Weitere Provider (OpenAI, Google Vertex AI) sind in Planung.',
  },
  {
    question: 'Wie werden Credits abgerechnet?',
    answer:
      'Credits werden pro API-Request abgezogen. Die Kosten hängen vom verwendeten Modell ab (z.B. Claude Opus = 10 Credits, Sonnet = 5 Credits). Die Abbuchung erfolgt atomar in einer Datenbank-Transaktion, sodass Sie nie mehr Credits ausgeben als verfügbar. Sie können Credits jederzeit nachkaufen oder ein Abo mit monatlichem Credit-Kontingent wählen. Credits verfallen nicht.',
  },
  {
    question: 'Ist die Plattform DSGVO-konform?',
    answer:
      'Ja, absolut. Wir hosten alle Daten auf EU-Servern (Supabase EU-Region), bieten vollständige Datentrennung durch Row-Level Security, automatische PII-Redaktion und umfassende Audit-Logs für alle Datenzugriffe. Wir haben eine AVV (Auftragsverarbeitungsvertrag) vorbereitet und erfüllen alle DSGVO-Anforderungen. Auf Wunsch bieten wir auch On-Premise-Deployment an.',
  },
  {
    question: 'Gibt es eine kostenlose Testphase?',
    answer:
      'Ja! Der Starter-Plan ist dauerhaft kostenlos und beinhaltet 100 Credits pro Monat. Das reicht für ca. 10-20 AI-Anfragen, um die Plattform ausgiebig zu testen. Sie können jederzeit upgraden, wenn Sie mehr Credits benötigen. Keine Kreditkarte erforderlich für die Anmeldung.',
  },
  {
    question: 'Kann ich die API in meine Software integrieren?',
    answer:
      'Ja, genau dafür ist die Plattform gemacht! Sie erhalten API-Keys, die Sie in Ihrer Anwendung verwenden können. Die API ist kompatibel mit der OpenAI/Anthropic SDK, sodass Sie meist nur die Base URL ändern müssen. Wir bieten auch Webhooks für Ereignisse (z.B. Credit-Warnung) und ausführliche Dokumentation mit Code-Beispielen in Python, JavaScript, TypeScript.',
  },
  {
    question: 'Was passiert bei Provider-Ausfall?',
    answer:
      'Unser System bietet automatisches Failover zwischen mehreren AI-Providern. Wenn Anthropic ausfällt oder Rate Limits erreicht, wechseln wir automatisch zu Scaleway (oder umgekehrt). Der Wechsel erfolgt transparent und innerhalb von Millisekunden. Sie können auch manuell Prioritäten festlegen, welcher Provider bevorzugt werden soll. So garantieren wir 99.9% Verfügbarkeit.',
  },
]

export function FAQ() {
  // Generate JSON-LD structured data for SEO
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((faq) => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer,
      },
    })),
  }

  return (
    <section id="faq" className="py-20 md:py-32">
      <div className="container">
        <div className="mx-auto max-w-3xl">
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
              Häufig gestellte Fragen
            </h2>
            <p className="text-lg text-muted-foreground">
              Alles, was Sie über AI Legal Ops wissen müssen
            </p>
          </div>

          <Accordion type="single" collapsible className="w-full">
            {faqs.map((faq, index) => (
              <AccordionItem key={index} value={`item-${index}`}>
                <AccordionTrigger className="text-left text-lg font-semibold">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-base leading-relaxed text-muted-foreground">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>

          <div className="mt-12 text-center">
            <p className="text-muted-foreground">
              Haben Sie weitere Fragen?{' '}
              <a
                href="/contact"
                className="font-medium text-primary hover:underline"
              >
                Kontaktieren Sie uns
              </a>
            </p>
          </div>
        </div>
      </div>

      {/* Schema.org structured data for SEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
    </section>
  )
}
