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
      'AI Legal Ops ist ein Enterprise-Grade AI Gateway, das als sicherer Proxy zwischen Ihrer Anwendung und verschiedenen AI-Providern agiert. Wir bieten automatische PII-Erkennung, Multi-Provider-Management, transparente Abrechnung und vollständige DSGVO-Compliance. Damit können Sie AI-Funktionen sicher in Ihre Anwendung integrieren, ohne sich um Datenschutz, Provider-Management oder Compliance kümmern zu müssen.',
  },
  {
    question: 'Ist der Service DSGVO-konform?',
    answer:
      'Ja, absolut. Wir erfüllen alle Anforderungen der DSGVO durch EU Data Residency (alle Daten werden auf deutschen Servern gespeichert), automatische PII-Redaktion durch unseren Privacy Shield, vollständige Datentrennung durch Row-Level Security und umfassende Audit-Logs für alle Datenzugriffe. Wir bieten eine vorbereitete AVV (Auftragsverarbeitungsvertrag) und auf Wunsch auch On-Premise-Deployment für maximale Kontrolle.',
  },
  {
    question: 'Welche KI-Modelle werden unterstützt?',
    answer:
      'Aktuell unterstützen wir Claude (Opus, Sonnet, Haiku) von Anthropic, sowie Llama 3.1 und Mixtral über Scaleway AI. Unser System bietet automatisches Failover: Wenn ein Provider ausfällt oder Rate Limits erreicht, wechseln wir nahtlos zum nächsten verfügbaren Provider. Weitere Modelle (OpenAI GPT-4, Google Gemini via Vertex AI) sind in Planung und werden in Kürze verfügbar sein.',
  },
  {
    question: 'Wie funktioniert der Privacy Shield?',
    answer:
      'Der Privacy Shield ist unser automatisches Datenschutz-System. Es scannt alle Anfragen vor dem Versand an AI-Provider und erkennt personenbezogene Daten wie E-Mail-Adressen, Telefonnummern, IBAN, Namen, Adressen und weitere PII-Daten. Diese werden durch Platzhalter ersetzt, an den AI-Provider gesendet, und in der Antwort wieder eingefügt. So bleiben Ihre Daten DSGVO-konform geschützt, während die AI-Funktionalität vollständig erhalten bleibt. Alles automatisch, ohne zusätzlichen Code.',
  },
  {
    question: 'Kann ich den Service in meine App integrieren?',
    answer:
      'Ja, genau dafür ist die Plattform gemacht! Nach der Anmeldung erhalten Sie API-Keys, die Sie in Ihrer Anwendung verwenden können. Die API ist kompatibel mit der OpenAI/Anthropic SDK, sodass Sie meist nur die Base URL ändern müssen. Wir bieten auch Webhooks für Ereignisse (z.B. Credit-Warnung, Compliance-Events) und ausführliche Dokumentation mit Code-Beispielen in Python, JavaScript, TypeScript, PHP und weiteren Sprachen. Die Integration dauert typischerweise weniger als 30 Minuten.',
  },
]

export function FAQSection() {
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
              {' '}oder schauen Sie in unsere{' '}
              <a
                href="/docs"
                className="font-medium text-primary hover:underline"
              >
                ausführliche Dokumentation
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
