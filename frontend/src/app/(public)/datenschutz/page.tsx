import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Datenschutzerklärung | AI Orchestra Gateway",
  description: "Datenschutzerklärung der AI Orchestra Gateway Plattform - Informationen über die Verarbeitung personenbezogener Daten gemäß DSGVO",
};

export default function DatenschutzPage() {
  return (
    <div className="container mx-auto py-12 px-4 max-w-4xl">
      <div className="prose prose-slate dark:prose-invert max-w-none">
        <h1 className="text-4xl font-bold mb-8">Datenschutzerklärung</h1>

        <p className="text-muted-foreground mb-8">
          Stand: Dezember 2025
        </p>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">1. Verantwortlicher</h2>
          <p className="mb-4">
            Verantwortlich für die Datenverarbeitung auf dieser Website ist:
          </p>
          <div className="bg-muted p-4 rounded-lg mb-4">
            <p className="mb-2"><strong>AI Orchestra Gateway</strong></p>
            <p className="mb-2">[Firmenname]</p>
            <p className="mb-2">[Straße und Hausnummer]</p>
            <p className="mb-2">[PLZ und Ort]</p>
            <p className="mb-2">E-Mail: <a href="mailto:privacy@ai-orchestra.de" className="text-primary hover:underline">privacy@ai-orchestra.de</a></p>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">2. Allgemeine Hinweise</h2>
          <p className="mb-4">
            Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen Daten
            passiert, wenn Sie unsere Website besuchen und unsere Dienste nutzen. Personenbezogene Daten sind alle
            Daten, mit denen Sie persönlich identifiziert werden können.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">3. Datenerfassung auf dieser Website</h2>

          <h3 className="text-xl font-semibold mb-3 mt-6">3.1 Registrierung und Anmeldung</h3>
          <p className="mb-4">
            Bei der Registrierung auf unserer Plattform werden folgende Daten erfasst:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li>E-Mail-Adresse (erforderlich für Login und Kommunikation)</li>
            <li>Passwort (verschlüsselt gespeichert)</li>
            <li>Firmenname (optional)</li>
            <li>Weitere Profildaten nach Ihrer Wahl</li>
          </ul>
          <p className="mb-4">
            <strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung)
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">3.2 API-Nutzung und Logdaten</h3>
          <p className="mb-4">
            Bei der Nutzung unserer API werden folgende Daten verarbeitet:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li>API-Anfragen und Antworten (ohne personenbezogene Inhalte)</li>
            <li>Zeitstempel der Anfragen</li>
            <li>Verwendete Credits und Nutzungsstatistiken</li>
            <li>IP-Adresse (anonymisiert nach 7 Tagen)</li>
          </ul>
          <p className="mb-4">
            <strong>Wichtig:</strong> Unsere "Privacy Shield"-Technologie entfernt automatisch alle
            personenbezogenen Daten (E-Mail, Telefon, IBAN) aus Ihren API-Anfragen, bevor diese an
            KI-Anbieter weitergeleitet werden.
          </p>
          <p className="mb-4">
            <strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung) und
            Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an Systemsicherheit)
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">3.3 Cookies und lokale Speicherung</h3>
          <p className="mb-4">
            Wir verwenden folgende Cookies:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li><strong>Erforderliche Cookies:</strong> Session-Management, Authentifizierung (Supabase)</li>
            <li><strong>Funktionale Cookies:</strong> Theme-Einstellungen (Dark Mode), Sprachauswahl</li>
          </ul>
          <p className="mb-4">
            Sie können Cookies in Ihren Browser-Einstellungen deaktivieren, dies kann jedoch die
            Funktionalität der Website einschränken.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">4. Weitergabe von Daten an Dritte</h2>

          <h3 className="text-xl font-semibold mb-3 mt-6">4.1 KI-Provider</h3>
          <p className="mb-4">
            Wir nutzen folgende KI-Anbieter zur Verarbeitung Ihrer Anfragen:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li><strong>Anthropic (Claude):</strong> USA - EU-US Data Privacy Framework zertifiziert</li>
            <li><strong>Scaleway AI:</strong> Frankreich (EU) - DSGVO-konform</li>
          </ul>
          <p className="mb-4">
            <strong>Wichtig:</strong> Alle personenbezogenen Daten werden durch unseren "Privacy Shield"
            automatisch entfernt, bevor Daten an KI-Provider übertragen werden.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">4.2 Zahlungsdienstleister</h3>
          <p className="mb-4">
            Für die Zahlungsabwicklung nutzen wir <strong>Stripe</strong> (Irland, EU).
            Stripe ist PCI-DSS Level 1 zertifiziert. Wir speichern keine Kreditkartendaten.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">4.3 Hosting und Datenbank</h3>
          <p className="mb-4">
            Unsere Dienste werden gehostet von:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li><strong>Supabase:</strong> EU-Region - DSGVO-konform</li>
            <li><strong>Vercel/AWS:</strong> EU-Region - DSGVO-konform</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">5. Ihre Rechte gemäß DSGVO</h2>
          <p className="mb-4">Sie haben folgende Rechte:</p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li><strong>Auskunft (Art. 15 DSGVO):</strong> Sie können Auskunft über Ihre gespeicherten Daten verlangen</li>
            <li><strong>Berichtigung (Art. 16 DSGVO):</strong> Sie können die Korrektur falscher Daten verlangen</li>
            <li><strong>Löschung (Art. 17 DSGVO):</strong> Sie können die Löschung Ihrer Daten verlangen</li>
            <li><strong>Einschränkung (Art. 18 DSGVO):</strong> Sie können die Einschränkung der Verarbeitung verlangen</li>
            <li><strong>Datenübertragbarkeit (Art. 20 DSGVO):</strong> Sie können Ihre Daten in einem strukturierten Format erhalten</li>
            <li><strong>Widerspruch (Art. 21 DSGVO):</strong> Sie können der Verarbeitung widersprechen</li>
            <li><strong>Beschwerde:</strong> Sie können sich bei einer Datenschutz-Aufsichtsbehörde beschweren</li>
          </ul>
          <p className="mb-4">
            Zur Ausübung Ihrer Rechte kontaktieren Sie uns unter:
            <a href="mailto:privacy@ai-orchestra.de" className="text-primary hover:underline ml-1">
              privacy@ai-orchestra.de
            </a>
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">6. Datensicherheit</h2>
          <p className="mb-4">
            Wir setzen technische und organisatorische Sicherheitsmaßnahmen ein, um Ihre Daten zu schützen:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li>SSL/TLS-Verschlüsselung für alle Datenübertragungen</li>
            <li>Verschlüsselte Speicherung von Passwörtern (bcrypt)</li>
            <li>Row-Level Security (RLS) in der Datenbank</li>
            <li>Automatische PII-Erkennung und -Entfernung</li>
            <li>Regelmäßige Security-Audits</li>
            <li>Zugriffsbeschränkungen und Audit-Logs</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">7. Speicherdauer</h2>
          <p className="mb-4">
            Wir speichern Ihre Daten nur so lange, wie es erforderlich ist:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li><strong>Kontodaten:</strong> Bis zur Löschung Ihres Kontos</li>
            <li><strong>Nutzungslogs:</strong> 90 Tage</li>
            <li><strong>IP-Adressen:</strong> 7 Tage (dann anonymisiert)</li>
            <li><strong>Rechnungsdaten:</strong> 10 Jahre (gesetzliche Aufbewahrungspflicht)</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">8. Besonderheiten für Geschäftskunden</h2>
          <p className="mb-4">
            Wenn Sie unsere Dienste im Rahmen einer Auftragsverarbeitung nutzen:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li>Wir schließen mit Ihnen einen Auftragsverarbeitungsvertrag (AVV) gemäß Art. 28 DSGVO</li>
            <li>Sie bleiben Verantwortlicher für die Datenverarbeitung</li>
            <li>Wir verarbeiten Daten nur nach Ihren Weisungen</li>
            <li>Technische und organisatorische Maßnahmen (TOMs) werden dokumentiert</li>
          </ul>
          <p className="mb-4">
            Für einen AVV kontaktieren Sie:
            <a href="mailto:legal@ai-orchestra.de" className="text-primary hover:underline ml-1">
              legal@ai-orchestra.de
            </a>
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">9. Änderungen der Datenschutzerklärung</h2>
          <p className="mb-4">
            Wir behalten uns vor, diese Datenschutzerklärung anzupassen, um sie an geänderte Rechtslagen
            oder Änderungen unserer Dienste anzupassen. Die jeweils aktuelle Version finden Sie auf dieser Seite.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">10. Kontakt</h2>
          <p className="mb-4">
            Bei Fragen zum Datenschutz kontaktieren Sie uns:
          </p>
          <div className="bg-muted p-4 rounded-lg">
            <p className="mb-2"><strong>E-Mail:</strong> <a href="mailto:privacy@ai-orchestra.de" className="text-primary hover:underline">privacy@ai-orchestra.de</a></p>
            <p className="mb-2"><strong>Datenschutzbeauftragter:</strong> dsb@ai-orchestra.de</p>
          </div>
        </section>

        <div className="mt-12 pt-8 border-t border-border">
          <p className="text-sm text-muted-foreground text-center">
            <Link href="/impressum" className="text-primary hover:underline">Impressum</Link>
            {" • "}
            <Link href="/agb" className="text-primary hover:underline">AGB</Link>
            {" • "}
            <Link href="/" className="text-primary hover:underline">Zurück zur Startseite</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
