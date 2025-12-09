import Link from 'next/link'
import { ReactNode } from 'react'

interface AuthLayoutProps {
  children: ReactNode
  title: string
  subtitle?: string
}

export function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left side - Branding/Image */}
      <div className="hidden lg:flex lg:flex-col lg:justify-between bg-gradient-to-br from-primary to-primary/80 p-12 text-primary-foreground">
        <div>
          <Link href="/" className="flex items-center gap-2 text-2xl font-bold">
            AI Legal Ops
          </Link>
        </div>

        <div className="space-y-4">
          <h1 className="text-4xl font-bold leading-tight">
            KI-gestützte Lösung für rechtliche Prozesse
          </h1>
          <p className="text-lg text-primary-foreground/80">
            Sichere, DSGVO-konforme AI-Integration für Ihre Geschäftsprozesse
          </p>
        </div>

        <div className="text-sm text-primary-foreground/60">
          © 2024 AI Legal Ops. Alle Rechte vorbehalten.
        </div>
      </div>

      {/* Right side - Form */}
      <div className="flex flex-col justify-center px-4 py-12 sm:px-6 lg:px-20 xl:px-24">
        <div className="mx-auto w-full max-w-sm">
          <div className="mb-8 lg:hidden">
            <Link href="/" className="inline-flex items-center gap-2 text-xl font-bold">
              AI Legal Ops
            </Link>
          </div>

          <div className="mb-8">
            <h2 className="text-3xl font-bold tracking-tight">{title}</h2>
            {subtitle && (
              <p className="mt-2 text-sm text-muted-foreground">{subtitle}</p>
            )}
          </div>

          {children}

          <div className="mt-8">
            <Link
              href="/"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              ← Zurück zur Startseite
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
