import { PublicHeader } from '@/components/layout/PublicHeader'
import { Footer } from '@/components/layout/Footer'
import { SkipLink } from '@/components/a11y/SkipLink'
import { CookieConsent } from '@/components/CookieConsent'

export default function LandingLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <SkipLink />
      <PublicHeader />
      <main id="main-content" className="flex-1">
        {children}
      </main>
      <Footer />
      <CookieConsent />
    </div>
  )
}
