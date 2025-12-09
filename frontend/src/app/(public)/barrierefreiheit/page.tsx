import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Erklärung zur Barrierefreiheit | AI Legal Ops Gateway',
  description: 'Erklärung zur Barrierefreiheit gemäß BITV 2.0 und EU-Richtlinie 2016/2102 für AI Legal Ops Gateway.',
};

export default function BarrierefreiheitPage() {
  const lastUpdated = '08.12.2025';

  return (
    <div className="container mx-auto max-w-4xl py-12">
      {/* Header */}
      <div className="mb-8 border-b pb-8">
        <h1 className="mb-4 text-4xl font-bold">Erklärung zur Barrierefreiheit</h1>
        <p className="text-sm text-muted-foreground">
          Stand: {lastUpdated}
        </p>
      </div>

      {/* Quick Access */}
      <div className="mb-8 rounded-lg border bg-primary/5 p-6">
        <h2 className="mb-2 text-lg font-semibold">Barrierefreiheits-Einstellungen</h2>
        <p className="mb-4 text-sm text-muted-foreground">
          Nutzen Sie das Barrierefreiheits-Panel, um die Website an Ihre Bedürfnisse anzupassen.
        </p>
        <button
          className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
          onClick={() => {
            // TODO: Implement accessibility panel opener
          }}
        >
          Barrierefreiheits-Panel öffnen
        </button>
      </div>

      {/* Content */}
      <article className="prose prose-slate max-w-none dark:prose-invert">
        <section className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">Bekenntnis zur Barrierefreiheit</h2>
          <p>
            AI Legal Ops GmbH ist bestrebt, ihre Website{' '}
            <a href="https://ailegalops.de" className="text-primary hover:underline">
              www.ailegalops.de
            </a>{' '}
            im Einklang mit den Bestimmungen der BITV 2.0 (Barrierefreie-Informationstechnik-Verordnung)
            sowie der EU-Richtlinie 2016/2102 über den barrierefreien Zugang zu Websites und
            mobilen Anwendungen öffentlicher Stellen barrierefrei zugänglich zu machen.
          </p>
          <p>
            Diese Erklärung zur Barrierefreiheit gilt für die Website www.ailegalops.de sowie
            alle zugehörigen Unterseiten und Anwendungen.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">Stand der Vereinbarkeit</h2>
          <p>
            Diese Website ist mit den folgenden Standards vereinbar:
          </p>
          <ul>
            <li>
              <strong>WCAG 2.1 Level AA</strong> (Web Content Accessibility Guidelines):
              Teilweise konform
            </li>
            <li>
              <strong>BITV 2.0</strong> (Barrierefreie-Informationstechnik-Verordnung):
              Teilweise konform
            </li>
            <li>
              <strong>EN 301 549</strong> (Europäische Norm für digitale Barrierefreiheit):
              Teilweise konform
            </li>
          </ul>
          <p>
            <em>Teilweise konform</em> bedeutet, dass einige Teile des Inhalts nicht vollständig
            den Barrierefreiheitsstandards entsprechen. Wir arbeiten kontinuierlich daran, die
            Barrierefreiheit unserer Website zu verbessern.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">Umgesetzte Maßnahmen</h2>
          <p>
            Zur Gewährleistung der Barrierefreiheit haben wir folgende Maßnahmen umgesetzt:
          </p>

          <h3 className="mb-2 text-xl font-semibold">Technische Barrierefreiheit</h3>
          <ul>
            <li>
              <strong>Semantisches HTML:</strong> Verwendung korrekter HTML-Elemente für
              bessere Screenreader-Kompatibilität
            </li>
            <li>
              <strong>ARIA-Labels:</strong> Einsatz von ARIA-Attributen zur Verbesserung der
              Zugänglichkeit interaktiver Elemente
            </li>
            <li>
              <strong>Tastaturnavigation:</strong> Vollständige Navigation mit der Tastatur
              möglich (Tab, Enter, Escape)
            </li>
            <li>
              <strong>Skip-Links:</strong> "Zum Hauptinhalt springen"-Links für schnellere
              Navigation
            </li>
            <li>
              <strong>Focus-Indikatoren:</strong> Deutlich sichtbare Fokus-Markierungen bei
              Tastaturnavigation
            </li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">Visuelle Barrierefreiheit</h3>
          <ul>
            <li>
              <strong>Farbkontraste:</strong> Kontrastverhältnisse gemäß WCAG 2.1 Level AA
              (mindestens 4.5:1 für Text)
            </li>
            <li>
              <strong>Schriftgrößen:</strong> Anpassbare Schriftgrößen über Browser-Zoom
              (bis 200% ohne Informationsverlust)
            </li>
            <li>
              <strong>Dark Mode:</strong> Dunkler Modus für bessere Lesbarkeit bei
              Lichtempfindlichkeit
            </li>
            <li>
              <strong>Keine reinen Farbcodierungen:</strong> Informationen werden nicht
              ausschließlich über Farben vermittelt
            </li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">Inhaltliche Barrierefreiheit</h3>
          <ul>
            <li>
              <strong>Alternative Texte:</strong> Alle Bilder haben beschreibende Alt-Texte
            </li>
            <li>
              <strong>Klare Struktur:</strong> Logische Überschriftenhierarchie (h1-h6)
            </li>
            <li>
              <strong>Verständliche Sprache:</strong> Einfache und klare Formulierungen
            </li>
            <li>
              <strong>Untertitel:</strong> Videos enthalten Untertitel (sofern vorhanden)
            </li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">Interaktive Funktionen</h3>
          <ul>
            <li>
              <strong>Formulare:</strong> Eindeutige Labels und Fehlermeldungen
            </li>
            <li>
              <strong>Zeitlimits:</strong> Keine automatischen Zeitlimits ohne Verlängerungsoption
            </li>
            <li>
              <strong>Bewegte Inhalte:</strong> Animationen können deaktiviert werden
              (prefers-reduced-motion)
            </li>
            <li>
              <strong>Modals/Dialoge:</strong> Fokus-Management und ESC-Taste zum Schließen
            </li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">Nicht barrierefreie Inhalte</h2>
          <p>
            Trotz unserer Bemühungen sind folgende Inhalte möglicherweise noch nicht
            vollständig barrierefrei:
          </p>

          <h3 className="mb-2 text-xl font-semibold">Bekannte Einschränkungen</h3>
          <ul>
            <li>
              <strong>PDF-Dokumente:</strong> Ältere PDF-Dokumente sind möglicherweise nicht
              vollständig barrierefrei aufbereitet. Wir arbeiten daran, alle PDFs nach
              PDF/UA-Standard zu optimieren.
            </li>
            <li>
              <strong>Externe Inhalte:</strong> Eingebettete Inhalte von Drittanbietern
              (z.B. YouTube-Videos) unterliegen der Barrierefreiheit des jeweiligen Anbieters.
            </li>
            <li>
              <strong>Komplexe Diagramme:</strong> Einige komplexe Visualisierungen verfügen
              noch nicht über vollständige Textalternativen.
            </li>
            <li>
              <strong>Admin-Dashboard:</strong> Der administrative Bereich wird schrittweise
              für Barrierefreiheit optimiert (voraussichtlich Q2 2026).
            </li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">Gründe für Ausnahmen</h3>
          <p>
            Die aufgeführten Einschränkungen sind bekannt und werden aus folgenden Gründen
            noch nicht vollständig behoben:
          </p>
          <ul>
            <li>Technische Abhängigkeiten von Drittanbietern</li>
            <li>Laufende Entwicklungsarbeiten (Roadmap bis Q2 2026)</li>
            <li>Unverhältnismäßiger Aufwand bei Legacy-Inhalten (werden sukzessive migriert)</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">Barrierefreiheits-Funktionen</h2>
          <p>
            Unsere Website bietet ein Barrierefreiheits-Panel mit folgenden Einstellungen:
          </p>

          <div className="rounded-lg border bg-muted/30 p-6">
            <h3 className="mb-4 text-lg font-semibold">Verfügbare Anpassungen</h3>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <h4 className="mb-2 font-semibold">Schriftgröße</h4>
                <ul className="text-sm">
                  <li>Klein (90%)</li>
                  <li>Normal (100%)</li>
                  <li>Groß (125%)</li>
                  <li>Sehr groß (150%)</li>
                </ul>
              </div>
              <div>
                <h4 className="mb-2 font-semibold">Kontrast</h4>
                <ul className="text-sm">
                  <li>Normal</li>
                  <li>Erhöhter Kontrast</li>
                  <li>Hoher Kontrast</li>
                </ul>
              </div>
              <div>
                <h4 className="mb-2 font-semibold">Animationen</h4>
                <ul className="text-sm">
                  <li>Aktiviert (Standard)</li>
                  <li>Reduziert</li>
                  <li>Deaktiviert</li>
                </ul>
              </div>
              <div>
                <h4 className="mb-2 font-semibold">Farbschema</h4>
                <ul className="text-sm">
                  <li>Hell</li>
                  <li>Dunkel</li>
                  <li>Automatisch</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">Erstellung dieser Erklärung</h2>
          <p>
            Diese Erklärung wurde am <strong>08.12.2025</strong> erstellt und zuletzt am{' '}
            <strong>{lastUpdated}</strong> überprüft.
          </p>
          <p>
            Die Erklärung wurde auf Grundlage einer Selbstbewertung erstellt. Eine externe
            Prüfung durch unabhängige Sachverständige ist für Q1 2026 geplant.
          </p>

          <h3 className="mb-2 text-xl font-semibold">Bewertungsmethodik</h3>
          <p>
            Die Bewertung erfolgte durch:
          </p>
          <ul>
            <li>Selbstbewertung anhand der WCAG 2.1 Richtlinien</li>
            <li>Automatisierte Tests mit Tools (axe DevTools, Lighthouse)</li>
            <li>Manuelle Tests mit Screenreadern (NVDA, VoiceOver)</li>
            <li>Tastaturnavigation-Tests</li>
            <li>Kontrastprüfungen (WebAIM Contrast Checker)</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">Feedback und Kontakt</h2>
          <p>
            Wir freuen uns über Ihr Feedback zur Barrierefreiheit unserer Website. Wenn Sie auf
            Barrieren stoßen oder Verbesserungsvorschläge haben, kontaktieren Sie uns bitte:
          </p>

          <div className="rounded-lg border bg-muted/30 p-6">
            <h3 className="mb-4 text-lg font-semibold">Kontaktmöglichkeiten</h3>
            <p>
              <strong>E-Mail:</strong>{' '}
              <a
                href="mailto:barrierefreiheit@ailegalops.de"
                className="text-primary hover:underline"
              >
                barrierefreiheit@ailegalops.de
              </a>
              <br />
              <strong>Telefon:</strong> +49 (0) 30 1234567-0 (Mo-Fr, 9-17 Uhr)
              <br />
              <strong>Kontaktformular:</strong>{' '}
              <Link href="/contact" className="text-primary hover:underline">
                www.ailegalops.de/contact
              </Link>
            </p>
            <p className="mt-4 text-sm text-muted-foreground">
              Wir bemühen uns, Ihre Anfrage innerhalb von 3 Werktagen zu beantworten und
              eine Lösung innerhalb von 10 Werktagen bereitzustellen.
            </p>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">Durchsetzungsverfahren</h2>
          <p>
            Bei nicht zufriedenstellenden Antworten auf Ihre Mitteilung oder Anfrage können
            Sie die Schlichtungsstelle nach § 16 BGG (Behindertengleichstellungsgesetz)
            einschalten:
          </p>

          <div className="rounded-lg border bg-muted/30 p-6">
            <h3 className="mb-2 text-lg font-semibold">Schlichtungsstelle BGG</h3>
            <p>
              Schlichtungsstelle nach dem Behindertengleichstellungsgesetz
              <br />
              bei dem Beauftragten der Bundesregierung für die Belange von Menschen mit
              Behinderungen
              <br />
              Mauerstraße 53
              <br />
              10117 Berlin
            </p>
            <p className="mt-4">
              <strong>Telefon:</strong> +49 (0) 30 18527-2805
              <br />
              <strong>Fax:</strong> +49 (0) 30 18527-2901
              <br />
              <strong>E-Mail:</strong>{' '}
              <a href="mailto:info@schlichtungsstelle-bgg.de" className="text-primary hover:underline">
                info@schlichtungsstelle-bgg.de
              </a>
              <br />
              <strong>Website:</strong>{' '}
              <a
                href="https://www.schlichtungsstelle-bgg.de"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                www.schlichtungsstelle-bgg.de
              </a>
            </p>
          </div>

          <p className="mt-4">
            Das Schlichtungsverfahren ist kostenlos. Sie benötigen keinen Rechtsbeistand.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">Roadmap zur Barrierefreiheit</h2>
          <p>
            Wir arbeiten kontinuierlich an der Verbesserung der Barrierefreiheit. Geplante
            Maßnahmen:
          </p>

          <div className="space-y-4">
            <div className="rounded-lg border-l-4 border-primary bg-muted/30 p-4">
              <h4 className="mb-1 font-semibold">Q1 2026</h4>
              <ul className="text-sm">
                <li>Externe WCAG 2.1 Level AA Zertifizierung</li>
                <li>Optimierung aller PDF-Dokumente nach PDF/UA</li>
                <li>Screenreader-Optimierung des Dashboards</li>
              </ul>
            </div>

            <div className="rounded-lg border-l-4 border-muted-foreground bg-muted/30 p-4">
              <h4 className="mb-1 font-semibold">Q2 2026</h4>
              <ul className="text-sm">
                <li>Vollständige WCAG 2.1 Level AAA Konformität (Ziel)</li>
                <li>Gebärdensprach-Videos für Hauptinhalte</li>
                <li>Erweiterte Textanpassungsoptionen</li>
              </ul>
            </div>

            <div className="rounded-lg border-l-4 border-muted-foreground bg-muted/30 p-4">
              <h4 className="mb-1 font-semibold">Laufend</h4>
              <ul className="text-sm">
                <li>Monatliche automatisierte Barrierefreiheits-Audits</li>
                <li>Quarterly manuelle Tests mit Assistenztechnologien</li>
                <li>Berücksichtigung von Nutzer-Feedback</li>
              </ul>
            </div>
          </div>
        </section>

        <div className="mt-12 rounded-lg border bg-primary/5 p-6">
          <h3 className="mb-2 text-lg font-semibold">
            Barrierefreiheit ist uns wichtig
          </h3>
          <p className="text-sm">
            Barrierefreiheit ist für uns kein "Nice-to-have", sondern ein fundamentales Recht.
            Wir sind verpflichtet, unsere digitalen Angebote für alle Menschen zugänglich zu
            machen, unabhängig von körperlichen oder technischen Voraussetzungen.
          </p>
          <p className="mt-2 text-sm">
            Wenn Sie Schwierigkeiten bei der Nutzung unserer Website haben, zögern Sie nicht,
            uns zu kontaktieren. Wir helfen Ihnen gerne weiter.
          </p>
        </div>
      </article>

      {/* Back to Home */}
      <div className="mt-12 border-t pt-8">
        <Link
          href="/"
          className="inline-flex items-center text-sm text-primary hover:underline"
        >
          ← Zurück zur Startseite
        </Link>
      </div>

      {/* Print Styles */}
      <style jsx>{`
        @media print {
          header,
          footer,
          .no-print {
            display: none;
          }
          .prose {
            max-width: none;
          }
        }
      `}</style>
    </div>
  );
}
