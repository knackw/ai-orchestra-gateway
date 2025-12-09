import type { Metadata } from 'next'
import { HeroSection } from '@/components/landing/HeroSection'
import { FeaturesSection } from '@/components/landing/FeaturesSection'
import { PricingSection } from '@/components/landing/PricingSection'
import { TestimonialsSection } from '@/components/landing/TestimonialsSection'
import { FAQSection } from '@/components/landing/FAQSection'

export const metadata: Metadata = {
  title: 'AI Legal Ops - KI-Power für Ihr Business, DSGVO-konform',
  description:
    'Enterprise-Grade AI Gateway mit Privacy Shield. Multi-Provider-Support (Anthropic, Scaleway, Vertex AI), automatische PII-Erkennung und 100% DSGVO-Compliance. Made in EU.',
  keywords: [
    'AI Gateway',
    'DSGVO',
    'Privacy Shield',
    'Multi-Provider AI',
    'Anthropic',
    'Claude',
    'Enterprise AI',
    'AI Compliance',
    'EU Data Residency',
    'AI Legal',
    'LegalTech',
    'PII Protection',
    'Data Privacy',
    'AI Proxy',
  ],
  authors: [{ name: 'AI Legal Ops' }],
  creator: 'AI Legal Ops',
  publisher: 'AI Legal Ops',
  openGraph: {
    type: 'website',
    locale: 'de_DE',
    url: 'https://ai-legal-ops.com',
    title: 'AI Legal Ops - KI-Power für Ihr Business, DSGVO-konform',
    description:
      'Enterprise-Grade AI Gateway mit Privacy Shield. Multi-Provider-Support, automatische PII-Erkennung und 100% DSGVO-Compliance.',
    siteName: 'AI Legal Ops',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'AI Legal Ops - Enterprise AI Gateway',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AI Legal Ops - KI-Power für Ihr Business, DSGVO-konform',
    description:
      'Enterprise-Grade AI Gateway mit Privacy Shield. Multi-Provider-Support und 100% DSGVO-Compliance.',
    images: ['/og-image.jpg'],
    creator: '@ailegalops',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  alternates: {
    canonical: 'https://ai-legal-ops.com',
    languages: {
      'de-DE': 'https://ai-legal-ops.com',
      'en-US': 'https://ai-legal-ops.com/en',
    },
  },
  verification: {
    google: 'your-google-verification-code',
    // yandex: 'your-yandex-verification-code',
    // yahoo: 'your-yahoo-verification-code',
  },
}

export default function LandingPage() {
  // Generate JSON-LD structured data for SEO
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: 'AI Legal Ops',
    description:
      'Enterprise-Grade AI Gateway mit Privacy Shield, Multi-Provider-Support und DSGVO-Compliance',
    applicationCategory: 'BusinessApplication',
    operatingSystem: 'Web',
    offers: {
      '@type': 'AggregateOffer',
      priceCurrency: 'EUR',
      lowPrice: '49',
      highPrice: '199',
      offerCount: '3',
    },
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: '4.9',
      ratingCount: '127',
      bestRating: '5',
      worstRating: '1',
    },
    provider: {
      '@type': 'Organization',
      name: 'AI Legal Ops',
      url: 'https://ai-legal-ops.com',
      logo: 'https://ai-legal-ops.com/logo.png',
      sameAs: [
        'https://twitter.com/ailegalops',
        'https://linkedin.com/company/ai-legal-ops',
        'https://github.com/ai-legal-ops',
      ],
    },
  }

  return (
    <>
      <div className="min-h-screen">
        <HeroSection />
        <FeaturesSection />
        <PricingSection />
        <TestimonialsSection />
        <FAQSection />
      </div>

      {/* Schema.org JSON-LD for SEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
    </>
  )
}
