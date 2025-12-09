'use client'

import * as React from 'react'
import Link from 'next/link'
import { Github, Linkedin, Twitter } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const footerLinks = {
  product: {
    title: 'Produkt',
    links: [
      { label: 'Features', href: '#features' },
      { label: 'Pricing', href: '#pricing' },
      { label: 'Changelog', href: '/changelog' },
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
    ],
  },
  company: {
    title: 'Unternehmen',
    links: [
      { label: 'Über uns', href: '/about' },
      { label: 'Kontakt', href: '/contact' },
      { label: 'Karriere', href: '/careers' },
      { label: 'Partner', href: '/partners' },
    ],
  },
  legal: {
    title: 'Legal',
    links: [
      { label: 'Impressum', href: '/impressum' },
      { label: 'Datenschutz', href: '/datenschutz' },
      { label: 'AGB', href: '/agb' },
      { label: 'Cookie-Einstellungen', href: '#cookie-settings' },
    ],
  },
}

const socialLinks = [
  { icon: Github, label: 'GitHub', href: 'https://github.com/ai-legal-ops' },
  { icon: Twitter, label: 'Twitter', href: 'https://twitter.com/ailegalops' },
  { icon: Linkedin, label: 'LinkedIn', href: 'https://linkedin.com/company/ai-legal-ops' },
]

export function Footer() {
  const [language, setLanguage] = React.useState('de')

  return (
    <footer className="border-t bg-background">
      <div className="container py-12 md:py-16">
        {/* Main footer content */}
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-5">
          {/* Brand column */}
          <div className="lg:col-span-1">
            <Link href="/" className="flex items-center space-x-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                <span className="text-lg font-bold text-primary-foreground">
                  AI
                </span>
              </div>
              <span className="font-bold">AI Legal Ops</span>
            </Link>
            <p className="mt-4 text-sm text-muted-foreground">
              Enterprise-Grade AI Gateway mit Datenschutz-Garantie.
              DSGVO-konform. Made in EU.
            </p>

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

          {/* Legal links */}
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
