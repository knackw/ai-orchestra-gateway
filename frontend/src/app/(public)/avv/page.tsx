import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Auftragsverarbeitungsvertrag (AVV) | AI Legal Ops Gateway',
  description: 'DSGVO-konformer Auftragsverarbeitungsvertrag gemäß Art. 28 DSGVO für AI Legal Ops Gateway.',
};

export default function AVVPage() {
  const lastUpdated = '08.12.2025';

  return (
    <div className="container mx-auto max-w-4xl py-12">
      {/* Header */}
      <div className="mb-8 border-b pb-8">
        <h1 className="mb-4 text-4xl font-bold">
          Auftragsverarbeitungsvertrag (AVV)
        </h1>
        <p className="mb-2 text-sm text-muted-foreground">
          Gemäß Art. 28 DSGVO
        </p>
        <p className="text-sm text-muted-foreground">
          Zuletzt aktualisiert: {lastUpdated}
        </p>
      </div>

      {/* Download/Accept Section */}
      <div className="mb-8 rounded-lg border bg-primary/5 p-6">
        <h2 className="mb-2 text-lg font-semibold">Digitaler AVV-Abschluss</h2>
        <p className="mb-4 text-sm text-muted-foreground">
          Dieser Auftragsverarbeitungsvertrag wird automatisch mit Ihrer Registrierung
          wirksam. Sie können den Vertrag jederzeit herunterladen und archivieren.
        </p>
        <div className="flex gap-4">
          <button className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90">
            AVV als PDF herunterladen
          </button>
          <button className="rounded-md border px-4 py-2 text-sm hover:bg-muted">
            Signierte Version anfordern
          </button>
        </div>
      </div>

      {/* Table of Contents */}
      <div className="mb-12 rounded-lg border bg-muted/50 p-6">
        <h2 className="mb-4 text-lg font-semibold">Inhaltsverzeichnis</h2>
        <nav className="space-y-2" aria-label="Inhaltsverzeichnis">
          <a href="#gegenstand" className="block text-sm text-primary hover:underline">
            1. Gegenstand und Dauer
          </a>
          <a href="#zweck" className="block text-sm text-primary hover:underline">
            2. Art und Zweck der Verarbeitung
          </a>
          <a href="#datenarten" className="block text-sm text-primary hover:underline">
            3. Art der personenbezogenen Daten
          </a>
          <a href="#kategorien" className="block text-sm text-primary hover:underline">
            4. Kategorien betroffener Personen
          </a>
          <a href="#pflichten" className="block text-sm text-primary hover:underline">
            5. Pflichten des Auftragsverarbeiters
          </a>
          <a href="#tom" className="block text-sm text-primary hover:underline">
            6. Technische und organisatorische Maßnahmen
          </a>
          <a href="#unterauftragnehmer" className="block text-sm text-primary hover:underline">
            7. Unterauftragnehmer
          </a>
          <a href="#rechte" className="block text-sm text-primary hover:underline">
            8. Rechte der betroffenen Personen
          </a>
          <a href="#loeschung" className="block text-sm text-primary hover:underline">
            9. Löschung und Rückgabe
          </a>
          <a href="#nachweis" className="block text-sm text-primary hover:underline">
            10. Nachweispflichten
          </a>
        </nav>
      </div>

      {/* Content */}
      <article className="prose prose-slate max-w-none dark:prose-invert">
        <div className="mb-8 rounded-lg border bg-muted/30 p-6">
          <h3 className="mb-2 text-lg font-semibold">Vertragsparteien</h3>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <p className="mb-1 text-sm font-semibold">Auftraggeber (Verantwortlicher)</p>
              <p className="text-sm text-muted-foreground">
                Der registrierte Kunde gemäß
                <br />
                den bei der Registrierung angegebenen Daten
              </p>
            </div>
            <div>
              <p className="mb-1 text-sm font-semibold">Auftragnehmer (Auftragsverarbeiter)</p>
              <p className="text-sm text-muted-foreground">
                AI Legal Ops GmbH
                <br />
                Musterstraße 123
                <br />
                10115 Berlin, Deutschland
              </p>
            </div>
          </div>
        </div>

        <section id="gegenstand" className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">1. Gegenstand und Dauer</h2>

          <h3 className="mb-2 text-xl font-semibold">1.1 Gegenstand</h3>
          <p>
            Dieser Vertrag regelt die Rechte und Pflichten der Vertragsparteien bei der
            Verarbeitung personenbezogener Daten im Rahmen der Nutzung des AI Legal Ops
            Gateway (nachfolgend "Plattform"). Der Auftragnehmer verarbeitet personenbezogene
            Daten ausschließlich im Auftrag und nach Weisung des Auftraggebers.
          </p>

          <h3 className="mb-2 text-xl font-semibold">1.2 Dauer</h3>
          <p>
            Dieser Vertrag tritt mit der Registrierung des Auftraggebers in Kraft und endet
            automatisch mit der Beendigung des Hauptvertrages (Nutzungsvertrag). Die
            Bestimmungen zur Löschung und Rückgabe von Daten gelten auch nach Vertragsende
            fort.
          </p>

          <h3 className="mb-2 text-xl font-semibold">1.3 Rangfolge</h3>
          <p>
            Dieser AVV ist Bestandteil des Hauptvertrages und geht den Regelungen in den AGB
            vor, soweit datenschutzrechtliche Fragen betroffen sind.
          </p>
        </section>

        <section id="zweck" className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">2. Art und Zweck der Verarbeitung</h2>

          <h3 className="mb-2 text-xl font-semibold">2.1 Verarbeitungstätigkeiten</h3>
          <p>
            Der Auftragnehmer verarbeitet personenbezogene Daten für folgende Zwecke:
          </p>
          <ul>
            <li>
              <strong>API-Gateway-Dienste:</strong> Weiterleitung von API-Anfragen an
              KI-Provider
            </li>
            <li>
              <strong>Privacy Shield:</strong> Erkennung und Pseudonymisierung von PII
              (personenbezogene Daten) vor der Weiterleitung
            </li>
            <li>
              <strong>Nutzungsverwaltung:</strong> Abrechnung, Credit-Management,
              Nutzungsstatistiken
            </li>
            <li>
              <strong>Logging und Monitoring:</strong> Protokollierung von API-Anfragen
              für Fehleranalyse und Sicherheit
            </li>
            <li>
              <strong>Technischer Support:</strong> Fehleranalyse und Kundenbetreuung
            </li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">2.2 Ort der Verarbeitung</h3>
          <p>
            Die Verarbeitung erfolgt in Rechenzentren innerhalb der Europäischen Union:
          </p>
          <ul>
            <li>Primärer Standort: Frankfurt am Main, Deutschland</li>
            <li>Backup-Standort: Paris, Frankreich</li>
            <li>Datenbank: Supabase (EU-Region)</li>
          </ul>
        </section>

        <section id="datenarten" className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">3. Art der personenbezogenen Daten</h2>
          <p>
            Folgende Kategorien personenbezogener Daten werden verarbeitet:
          </p>

          <h3 className="mb-2 text-xl font-semibold">3.1 Bestandsdaten des Auftraggebers</h3>
          <ul>
            <li>Firmenname / Name</li>
            <li>Adresse</li>
            <li>Kontaktperson</li>
            <li>E-Mail-Adresse</li>
            <li>Telefonnummer</li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">3.2 Nutzungsdaten</h3>
          <ul>
            <li>Benutzername / User-ID</li>
            <li>API-Keys und Zugangstoken</li>
            <li>Zeitstempel der API-Nutzung</li>
            <li>IP-Adressen</li>
            <li>Nutzungsstatistiken (Credits, Anfragen)</li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">3.3 Inhaltsdaten (vom Auftraggeber übermittelt)</h3>
          <ul>
            <li>API-Request-Payloads (Textinhalte, Prompts)</li>
            <li>API-Response-Daten (KI-generierte Antworten)</li>
            <li>Ggf. darin enthaltene personenbezogene Daten der Endnutzer des Auftraggebers</li>
          </ul>
          <p>
            <strong>Hinweis:</strong> Der Auftragnehmer wendet Privacy-Shield-Technologie an,
            um PII in Inhaltsdaten automatisch zu erkennen und zu pseudonymisieren, bevor
            diese an Unterauftragnehmer (KI-Provider) weitergeleitet werden.
          </p>

          <h3 className="mb-2 text-xl font-semibold">3.4 Zahlungsdaten</h3>
          <ul>
            <li>Rechnungsadresse</li>
            <li>Zahlungsinformationen (über Zahlungsdienstleister verarbeitet)</li>
          </ul>
        </section>

        <section id="kategorien" className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">4. Kategorien betroffener Personen</h2>
          <ul>
            <li>
              <strong>Mitarbeiter des Auftraggebers:</strong> Nutzer, Administratoren
            </li>
            <li>
              <strong>Endnutzer des Auftraggebers:</strong> Personen, deren Daten vom
              Auftraggeber über die Plattform verarbeitet werden
            </li>
            <li>
              <strong>Geschäftspartner des Auftraggebers:</strong> Soweit deren Daten
              übermittelt werden
            </li>
          </ul>
        </section>

        <section id="pflichten" className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">5. Pflichten des Auftragsverarbeiters</h2>

          <h3 className="mb-2 text-xl font-semibold">5.1 Weisungsgebundenheit</h3>
          <p>
            Der Auftragnehmer verarbeitet personenbezogene Daten ausschließlich nach den
            dokumentierten Weisungen des Auftraggebers. Die Nutzung der Plattform gemäß den
            AGB und dieser AVV gilt als dokumentierte Weisung.
          </p>
          <p>
            Der Auftragnehmer informiert den Auftraggeber unverzüglich, wenn er der Ansicht
            ist, dass eine Weisung gegen datenschutzrechtliche Vorschriften verstößt.
          </p>

          <h3 className="mb-2 text-xl font-semibold">5.2 Vertraulichkeit</h3>
          <p>
            Der Auftragnehmer verpflichtet sich, die Vertraulichkeit personenbezogener Daten
            zu wahren. Alle mit der Verarbeitung betrauten Personen wurden auf die
            Vertraulichkeit verpflichtet oder unterliegen einer entsprechenden gesetzlichen
            Verschwiegenheitspflicht.
          </p>

          <h3 className="mb-2 text-xl font-semibold">5.3 Datensicherheit</h3>
          <p>
            Der Auftragnehmer trifft alle erforderlichen technischen und organisatorischen
            Maßnahmen gemäß Art. 32 DSGVO, um ein dem Risiko angemessenes Schutzniveau zu
            gewährleisten (siehe Abschnitt 6).
          </p>

          <h3 className="mb-2 text-xl font-semibold">5.4 Unterstützungspflichten</h3>
          <p>
            Der Auftragnehmer unterstützt den Auftraggeber bei:
          </p>
          <ul>
            <li>
              Der Beantwortung von Anträgen betroffener Personen auf Wahrnehmung ihrer Rechte
              (Auskunft, Berichtigung, Löschung, etc.)
            </li>
            <li>
              Der Einhaltung der Pflichten aus Art. 32-36 DSGVO (Sicherheit, Meldung von
              Datenschutzverletzungen, Datenschutz-Folgenabschätzung)
            </li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">5.5 Meldung von Datenschutzverletzungen</h3>
          <p>
            Der Auftragnehmer meldet dem Auftraggeber unverzüglich (innerhalb von 24 Stunden)
            jede Verletzung des Schutzes personenbezogener Daten und stellt alle erforderlichen
            Informationen zur Verfügung, damit der Auftraggeber seiner Meldepflicht gemäß
            Art. 33 DSGVO nachkommen kann.
          </p>
        </section>

        <section id="tom" className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">
            6. Technische und organisatorische Maßnahmen (TOM)
          </h2>
          <p>
            Der Auftragnehmer hat folgende technische und organisatorische Maßnahmen gemäß
            Art. 32 DSGVO implementiert:
          </p>

          <h3 className="mb-2 text-xl font-semibold">6.1 Vertraulichkeit (Art. 32 Abs. 1 lit. b DSGVO)</h3>
          <ul>
            <li>
              <strong>Zutrittskontrolle:</strong> Physische Sicherung der Rechenzentren durch
              zertifizierte Hosting-Provider (ISO 27001)
            </li>
            <li>
              <strong>Zugangskontrolle:</strong> Authentifizierung via Benutzername/Passwort,
              Optional: Zwei-Faktor-Authentifizierung (2FA)
            </li>
            <li>
              <strong>Zugriffskontrolle:</strong> Rollenbasierte Zugriffskontrolle (RBAC),
              Least-Privilege-Prinzip
            </li>
            <li>
              <strong>Trennungskontrolle:</strong> Multi-Tenant-Architektur mit strikter
              Datenisolierung (Row Level Security)
            </li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">6.2 Integrität (Art. 32 Abs. 1 lit. b DSGVO)</h3>
          <ul>
            <li>
              <strong>Weitergabekontrolle:</strong> TLS 1.3 Verschlüsselung für alle
              Datenübertragungen
            </li>
            <li>
              <strong>Eingabekontrolle:</strong> Audit-Logging aller relevanten Operationen,
              unveränderliche Log-Einträge
            </li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">6.3 Verfügbarkeit (Art. 32 Abs. 1 lit. b DSGVO)</h3>
          <ul>
            <li>
              <strong>Verfügbarkeitskontrolle:</strong> Redundante Systeme, automatische
              Failover-Mechanismen
            </li>
            <li>
              <strong>Datensicherung:</strong> Tägliche automatisierte Backups,
              verschlüsselte Speicherung, geografisch getrennte Backup-Standorte
            </li>
            <li>
              <strong>Wiederherstellung:</strong> Disaster Recovery Plan, RTO: 4 Stunden,
              RPO: 24 Stunden
            </li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">6.4 Belastbarkeit (Art. 32 Abs. 1 lit. b DSGVO)</h3>
          <ul>
            <li>
              <strong>Monitoring:</strong> 24/7 Überwachung der Systemverfügbarkeit und
              Sicherheitsereignisse
            </li>
            <li>
              <strong>Incident Response:</strong> Dokumentiertes Verfahren zur Behandlung
              von Sicherheitsvorfällen
            </li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">6.5 Datenschutz durch Technik</h3>
          <ul>
            <li>
              <strong>Privacy Shield:</strong> Automatische Erkennung und Pseudonymisierung
              von PII vor Weiterleitung an KI-Provider
            </li>
            <li>
              <strong>Datenminimierung:</strong> Nur notwendige Daten werden verarbeitet
            </li>
            <li>
              <strong>Verschlüsselung:</strong> Sensitive Daten werden verschlüsselt
              gespeichert (AES-256)
            </li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">6.6 Verfahren zur Überprüfung</h3>
          <ul>
            <li>Jährliche interne Audits der TOM</li>
            <li>Penetrationstests durch externe Sicherheitsexperten</li>
            <li>Regelmäßige Überprüfung und Aktualisierung der Sicherheitsmaßnahmen</li>
          </ul>
        </section>

        <section id="unterauftragnehmer" className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">7. Unterauftragnehmer</h2>

          <h3 className="mb-2 text-xl font-semibold">7.1 Einwilligung</h3>
          <p>
            Der Auftraggeber erteilt dem Auftragnehmer die generelle Genehmigung, weitere
            Auftragsverarbeiter (Unterauftragnehmer) einzusetzen. Der Auftragnehmer informiert
            den Auftraggeber über beabsichtigte Änderungen mit einer Frist von 30 Tagen.
          </p>

          <h3 className="mb-2 text-xl font-semibold">7.2 Liste der Unterauftragnehmer</h3>
          <p>
            Aktuell werden folgende Unterauftragnehmer eingesetzt:
          </p>

          <div className="overflow-x-auto">
            <table className="min-w-full border">
              <thead className="bg-muted">
                <tr>
                  <th className="border px-4 py-2 text-left text-sm font-semibold">
                    Unterauftragnehmer
                  </th>
                  <th className="border px-4 py-2 text-left text-sm font-semibold">
                    Dienstleistung
                  </th>
                  <th className="border px-4 py-2 text-left text-sm font-semibold">
                    Standort
                  </th>
                </tr>
              </thead>
              <tbody className="text-sm">
                <tr>
                  <td className="border px-4 py-2">Supabase Inc.</td>
                  <td className="border px-4 py-2">Datenbank-Hosting</td>
                  <td className="border px-4 py-2">EU (Frankfurt)</td>
                </tr>
                <tr>
                  <td className="border px-4 py-2">Vercel Inc.</td>
                  <td className="border px-4 py-2">Application Hosting</td>
                  <td className="border px-4 py-2">EU (Frankfurt)</td>
                </tr>
                <tr>
                  <td className="border px-4 py-2">Anthropic PBC</td>
                  <td className="border px-4 py-2">KI-API (Claude)</td>
                  <td className="border px-4 py-2">USA (SCC)</td>
                </tr>
                <tr>
                  <td className="border px-4 py-2">Scaleway SAS</td>
                  <td className="border px-4 py-2">KI-API</td>
                  <td className="border px-4 py-2">Frankreich (EU)</td>
                </tr>
                <tr>
                  <td className="border px-4 py-2">Stripe Inc.</td>
                  <td className="border px-4 py-2">Zahlungsabwicklung</td>
                  <td className="border px-4 py-2">USA (SCC)</td>
                </tr>
              </tbody>
            </table>
          </div>

          <p className="mt-4">
            <strong>Hinweis:</strong> Die aktuelle Liste ist jederzeit im Dashboard unter
            "Einstellungen → Unterauftragnehmer" einsehbar.
          </p>

          <h3 className="mb-2 text-xl font-semibold">7.3 Verpflichtungen</h3>
          <p>
            Der Auftragnehmer stellt sicher, dass:
          </p>
          <ul>
            <li>
              Mit allen Unterauftragnehmern Verträge geschlossen wurden, die dieselben
              Datenschutzpflichten wie in diesem AVV enthalten
            </li>
            <li>
              Die Einhaltung der Datenschutzpflichten durch Unterauftragnehmer regelmäßig
              überprüft wird
            </li>
            <li>
              Der Auftragnehmer gegenüber dem Auftraggeber für die Einhaltung der
              Datenschutzpflichten durch Unterauftragnehmer haftet
            </li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">7.4 Widerspruchsrecht</h3>
          <p>
            Der Auftraggeber kann innerhalb von 14 Tagen nach Benachrichtigung der Hinzuziehung
            eines neuen Unterauftragnehmers Widerspruch einlegen, wenn er begründete Bedenken
            bezüglich der Datenschutz-Compliance hat.
          </p>
        </section>

        <section id="rechte" className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">8. Rechte der betroffenen Personen</h2>

          <h3 className="mb-2 text-xl font-semibold">8.1 Unterstützung bei Betroffenenrechten</h3>
          <p>
            Der Auftragnehmer unterstützt den Auftraggeber mit geeigneten technischen und
            organisatorischen Maßnahmen bei der Erfüllung von Anträgen betroffener Personen
            auf Wahrnehmung ihrer Rechte gemäß Kapitel III DSGVO:
          </p>
          <ul>
            <li>Auskunftsrecht (Art. 15 DSGVO)</li>
            <li>Recht auf Berichtigung (Art. 16 DSGVO)</li>
            <li>Recht auf Löschung (Art. 17 DSGVO)</li>
            <li>Recht auf Einschränkung der Verarbeitung (Art. 18 DSGVO)</li>
            <li>Recht auf Datenübertragbarkeit (Art. 20 DSGVO)</li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">8.2 Weiterleitung von Anfragen</h3>
          <p>
            Anfragen betroffener Personen, die direkt an den Auftragnehmer gerichtet werden,
            werden unverzüglich an den Auftraggeber weitergeleitet, soweit eine Zuordnung
            möglich ist.
          </p>

          <h3 className="mb-2 text-xl font-semibold">8.3 Self-Service-Tools</h3>
          <p>
            Der Auftragnehmer stellt im Dashboard Self-Service-Funktionen bereit, mit denen
            der Auftraggeber eigenständig Daten abrufen, korrigieren oder löschen kann.
          </p>
        </section>

        <section id="loeschung" className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">9. Löschung und Rückgabe von Daten</h2>

          <h3 className="mb-2 text-xl font-semibold">9.1 Löschung nach Vertragsende</h3>
          <p>
            Nach Beendigung des Hauptvertrages löscht der Auftragnehmer alle personenbezogenen
            Daten des Auftraggebers innerhalb von 30 Tagen, es sei denn, gesetzliche
            Aufbewahrungspflichten erfordern eine längere Speicherung.
          </p>

          <h3 className="mb-2 text-xl font-semibold">9.2 Datenexport vor Vertragsende</h3>
          <p>
            Der Auftraggeber hat das Recht, vor Vertragsende alle seine Daten über die
            Export-Funktion im Dashboard in einem strukturierten, gängigen und
            maschinenlesbaren Format (JSON, CSV) herunterzuladen.
          </p>

          <h3 className="mb-2 text-xl font-semibold">9.3 Bestätigung der Löschung</h3>
          <p>
            Auf Anfrage bestätigt der Auftragnehmer die vollständige Löschung aller Daten
            schriftlich. Dies umfasst auch die Löschung bei Unterauftragnehmern.
          </p>

          <h3 className="mb-2 text-xl font-semibold">9.4 Ausnahmen</h3>
          <p>
            Ausgenommen von der Löschungspflicht sind:
          </p>
          <ul>
            <li>
              Daten, die aufgrund gesetzlicher Aufbewahrungspflichten gespeichert werden
              müssen (z.B. Rechnungsdaten für 10 Jahre)
            </li>
            <li>
              Anonymisierte Daten für statistische Zwecke, die keinen Personenbezug mehr
              aufweisen
            </li>
          </ul>
        </section>

        <section id="nachweis" className="mb-8">
          <h2 className="mb-4 text-2xl font-bold">10. Nachweispflichten und Kontrollen</h2>

          <h3 className="mb-2 text-xl font-semibold">10.1 Nachweispflichten</h3>
          <p>
            Der Auftragnehmer führt ein Verzeichnis aller Kategorien von im Auftrag des
            Auftraggebers durchgeführten Verarbeitungstätigkeiten gemäß Art. 30 Abs. 2 DSGVO.
          </p>

          <h3 className="mb-2 text-xl font-semibold">10.2 Kontrollrechte</h3>
          <p>
            Der Auftraggeber hat das Recht, die Einhaltung der Datenschutzbestimmungen durch
            den Auftragnehmer zu kontrollieren. Dies umfasst:
          </p>
          <ul>
            <li>
              Einsicht in relevante Dokumentationen (TOM, Verarbeitungsverzeichnis)
            </li>
            <li>
              Durchführung von Audits nach vorheriger Ankündigung (14 Tage)
            </li>
            <li>
              Beauftragung externer Auditoren (auf Kosten des Auftraggebers)
            </li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">10.3 Informationspflichten</h3>
          <p>
            Der Auftragnehmer informiert den Auftraggeber unverzüglich über:
          </p>
          <ul>
            <li>Datenschutzverletzungen</li>
            <li>Wesentliche Änderungen der TOM</li>
            <li>Behördliche Anordnungen bezüglich der verarbeiteten Daten</li>
            <li>Kontrollen durch Aufsichtsbehörden</li>
          </ul>

          <h3 className="mb-2 text-xl font-semibold">10.4 Zertifizierungen</h3>
          <p>
            Der Auftragnehmer verfügt über folgende Zertifizierungen bzw. plant deren
            Erlangung:
          </p>
          <ul>
            <li>ISO 27001 (Informationssicherheit) - über Hosting-Provider</li>
            <li>SOC 2 Type II (geplant für 2026)</li>
          </ul>
        </section>

        <div className="mt-12 rounded-lg border bg-primary/5 p-6">
          <h3 className="mb-2 text-lg font-semibold">Vertragsabschluss und Gültigkeit</h3>
          <p className="text-sm">
            Dieser Auftragsverarbeitungsvertrag wird mit der Registrierung und Nutzung der
            Plattform automatisch wirksam. Die aktuelle Version ist jederzeit unter
            <Link href="/avv" className="mx-1 text-primary hover:underline">
              https://ailegalops.de/avv
            </Link>
            abrufbar.
          </p>
          <p className="mt-2 text-sm">
            Änderungen dieses AVV werden dem Auftraggeber mit einer Frist von 30 Tagen
            mitgeteilt. Der Auftraggeber hat das Recht, bei wesentlichen Änderungen den
            Vertrag außerordentlich zu kündigen.
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
