import { PublicHeader } from '@/components/layout/PublicHeader';
import { PublicFooter } from '@/components/layout/PublicFooter';
import { SkipLink } from '@/components/a11y/SkipLink';
import { AccessibilityPanel } from '@/components/a11y/AccessibilityPanel';
import { CookieConsent } from '@/components/CookieConsent';

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <SkipLink />
      <PublicHeader />
      <main id="main-content" className="flex-1" tabIndex={-1}>
        {children}
      </main>
      <PublicFooter />
      <AccessibilityPanel />
      <CookieConsent />
    </div>
  );
}
