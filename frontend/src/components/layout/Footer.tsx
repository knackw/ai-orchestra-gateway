'use client'

import * as React from 'react'
import Link from 'next/link'
import { Github, Linkedin, Twitter, Mail, ArrowRight } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { cn } from '@/lib/utils'

const footerLinks = {
  product: {
    title: 'Produkt',
    links: [
      { label: 'Features', href: '#features' },
      { label: 'Pricing', href: '#pricing' },
      { label: 'Changelog', href: '/changelog' },
      { label: 'Roadmap', href: '/roadmap' },
      { label: 'Status', href: '/status' },
    ],
  },
  resources: {
    title: 'Ressourcen',
    links: [
      { label: 'Dokumentation', href: '/docs' },
      { label: 'API Reference', href: '/docs/api' },
      { label: 'Blog', href: '/blog' },
      { label: 'Help Center', href: '/help' },
      { label: 'Beispiele', href: '/docs/examples' },
    ],
  },
  company: {
    title: 'Unternehmen',
    links: [
      { label: 'Über uns', href: '/about' },
      { label: 'Kontakt', href: '/contact' },
      { label: 'Karriere', href: '/careers' },
      { label: 'Partner', href: '/partners' },
      { label: 'Presse', href: '/press' },
    ],
  },
  legal: {
    title: 'Rechtliches',
    links: [
      { label: 'Impressum', href: '/impressum' },
      { label: 'Datenschutz', href: '/datenschutz' },
      { label: 'AGB', href: '/agb' },
      { label: 'AVV', href: '/avv' },
      { label: 'Cookie-Richtlinie', href: '/cookies' },
    ],
  },
  support: {
    title: 'Support',
    links: [
      { label: 'FAQ', href: '#faq' },
      { label: 'Community Forum', href: '/community' },
      { label: 'Support Portal', href: '/support' },
      { label: 'Service Status', href: '/status' },
      { label: 'Security', href: '/security' },
    ],
  },
}

const socialLinks = [
  {
    icon: Github,
    label: 'GitHub',
    href: 'https://github.com/ai-legal-ops',
    hoverColor: 'hover:text-[#181717]'
  },
  {
    icon: Twitter,
    label: 'Twitter',
    href: 'https://twitter.com/ailegalops',
    hoverColor: 'hover:text-[#1DA1F2]'
  },
  {
    icon: Linkedin,
    label: 'LinkedIn',
    href: 'https://linkedin.com/company/ai-legal-ops',
    hoverColor: 'hover:text-[#0A66C2]'
  },
  {
    icon: Mail,
    label: 'E-Mail',
    href: 'mailto:info@ai-legal-ops.com',
    hoverColor: 'hover:text-primary'
  },
]

export function Footer() {
  const [language, setLanguage] = React.useState('de')
  const [email, setEmail] = React.useState('')
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [submitMessage, setSubmitMessage] = React.useState('')

  const handleNewsletterSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setSubmitMessage('')

    try {
      // TODO: Implement newsletter subscription API call
      // const response = await fetch('/api/newsletter/subscribe', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email, language }),
      // })

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000))

      setSubmitMessage('Vielen Dank! Bitte bestätigen Sie Ihre E-Mail-Adresse.')
      setEmail('')
    } catch {
      setSubmitMessage('Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <footer className="border-t bg-background">
      <div className="container py-12 md:py-16">
        {/* Main footer content */}
        <div className="grid gap-8 lg:grid-cols-6">
          {/* Brand column with newsletter */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center space-x-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <span className="text-xl font-bold text-primary-foreground">
                  AI
                </span>
              </div>
              <span className="text-lg font-bold">AI Legal Ops</span>
            </Link>
            <p className="mt-4 text-sm text-muted-foreground">
              Enterprise-Grade AI Gateway mit Datenschutz-Garantie.
              <br />
              DSGVO-konform. Made in EU.
            </p>

            {/* Newsletter Signup */}
            <div className="mt-6">
              <h3 className="mb-3 text-sm font-semibold">Newsletter</h3>
              <p className="mb-3 text-sm text-muted-foreground">
                Bleiben Sie auf dem Laufenden über neue Features und Updates.
              </p>
              <form onSubmit={handleNewsletterSubmit} className="space-y-2">
                <div className="flex gap-2">
                  <Input
                    type="email"
                    placeholder="ihre@email.de"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    disabled={isSubmitting}
                    className="flex-1"
                  />
                  <Button
                    type="submit"
                    size="icon"
                    disabled={isSubmitting}
                    className="shrink-0"
                  >
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </div>
                {submitMessage && (
                  <p className={cn(
                    "text-xs",
                    submitMessage.includes('Fehler')
                      ? 'text-destructive'
                      : 'text-green-600'
                  )}>
                    {submitMessage}
                  </p>
                )}
              </form>
            </div>

            {/* Social links */}
            <div className="mt-6 flex gap-2">
              {socialLinks.map((social) => {
                const Icon = social.icon
                return (
                  <Button
                    key={social.label}
                    variant="ghost"
                    size="icon"
                    asChild
                    className={cn("transition-colors", social.hoverColor)}
                  >
                    <a
                      href={social.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label={social.label}
                    >
                      <Icon className="h-5 w-5" />
                    </a>
                  </Button>
                )
              })}
            </div>
          </div>

          {/* Product links */}
          <div>
            <h3 className="mb-4 text-sm font-semibold">
              {footerLinks.product.title}
            </h3>
            <ul className="space-y-3">
              {footerLinks.product.links.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-primary"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources links */}
          <div>
            <h3 className="mb-4 text-sm font-semibold">
              {footerLinks.resources.title}
            </h3>
            <ul className="space-y-3">
              {footerLinks.resources.links.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-primary"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company links */}
          <div>
            <h3 className="mb-4 text-sm font-semibold">
              {footerLinks.company.title}
            </h3>
            <ul className="space-y-3">
              {footerLinks.company.links.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-primary"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal & Support combined */}
          <div>
            <h3 className="mb-4 text-sm font-semibold">
              {footerLinks.legal.title}
            </h3>
            <ul className="space-y-3">
              {footerLinks.legal.links.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-primary"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom section */}
        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t pt-8 md:flex-row">
          {/* Copyright */}
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} AI Legal Ops. Alle Rechte vorbehalten.
          </p>

          {/* Language selector */}
          <Select value={language} onValueChange={setLanguage}>
            <SelectTrigger className="w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="de">🇩🇪 Deutsch</SelectItem>
              <SelectItem value="en">🇬🇧 English</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </footer>
  )
}
