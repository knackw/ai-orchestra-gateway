import Link from 'next/link';

export function PublicFooter() {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    product: [
      { name: 'Features', href: '/#features' },
      { name: 'Preise', href: '/#pricing' },
      { name: 'Dokumentation', href: '/#docs' },
      { name: 'API', href: '/api/docs' },
    ],
    legal: [
      { name: 'AGB', href: '/agb' },
      { name: 'Datenschutz', href: '/datenschutz' },
      { name: 'Impressum', href: '/impressum' },
      { name: 'AVV', href: '/avv' },
      { name: 'Barrierefreiheit', href: '/barrierefreiheit' },
    ],
    company: [
      { name: 'Über uns', href: '/about' },
      { name: 'Blog', href: '/blog' },
      { name: 'Kontakt', href: '/contact' },
      { name: 'Support', href: '/support' },
    ],
  };

  return (
    <footer className="border-t bg-background">
      <div className="container py-12">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          {/* Company Info */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                <span className="text-lg font-bold text-primary-foreground">AI</span>
              </div>
              <span className="font-bold">AI Legal Ops</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Sichere KI-Integration mit Datenschutz und Compliance für deutsche Unternehmen.
            </p>
          </div>

          {/* Product Links */}
          <div>
            <h3 className="mb-4 text-sm font-semibold">Produkt</h3>
            <ul className="space-y-3">
              {footerLinks.product.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h3 className="mb-4 text-sm font-semibold">Rechtliches</h3>
            <ul className="space-y-3">
              {footerLinks.legal.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="mb-4 text-sm font-semibold">Unternehmen</h3>
            <ul className="space-y-3">
              {footerLinks.company.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 border-t pt-8">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <p className="text-sm text-muted-foreground">
              © {currentYear} AI Legal Ops Gateway. Alle Rechte vorbehalten.
            </p>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-muted-foreground">🇩🇪 Made in Germany</span>
              <span className="text-sm text-muted-foreground">DSGVO-konform</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
