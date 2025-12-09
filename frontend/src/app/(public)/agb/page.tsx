import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "AGB - Allgemeine Geschäftsbedingungen | AI Orchestra Gateway",
  description: "Allgemeine Geschäftsbedingungen für die Nutzung der AI Orchestra Gateway Plattform",
};

export default function AGBPage() {
  return (
    <div className="container mx-auto py-12 px-4 max-w-4xl">
      <div className="prose prose-slate dark:prose-invert max-w-none">
        <h1 className="text-4xl font-bold mb-8">Allgemeine Geschäftsbedingungen (AGB)</h1>

        <p className="text-muted-foreground mb-8">
          Stand: Dezember 2025
        </p>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">1. Geltungsbereich</h2>

          <h3 className="text-xl font-semibold mb-3 mt-6">1.1 Anwendungsbereich</h3>
          <p className="mb-4">
            Diese Allgemeinen Geschäftsbedingungen (AGB) gelten für alle Verträge über die Nutzung der
            KI-Gateway-Dienste der <strong>AI Orchestra Gateway</strong> (nachfolgend "Anbieter" genannt)
            mit Kunden (nachfolgend "Nutzer" genannt).
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">1.2 Vertragssprache</h3>
          <p className="mb-4">
            Die Vertragssprache ist Deutsch. Übersetzungen dieser AGB dienen lediglich der Orientierung.
            Im Zweifel gilt die deutsche Fassung.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">1.3 Abweichende Bedingungen</h3>
          <p className="mb-4">
            Abweichende, entgegenstehende oder ergänzende Allgemeine Geschäftsbedingungen des Nutzers
            werden nicht Vertragsbestandteil, es sei denn, der Anbieter stimmt ihrer Geltung ausdrücklich
            schriftlich zu.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">2. Leistungsbeschreibung</h2>

          <h3 className="text-xl font-semibold mb-3 mt-6">2.1 Dienste</h3>
          <p className="mb-4">
            Der Anbieter stellt eine Cloud-basierte Gateway-Plattform bereit, über die Nutzer API-Anfragen
            an verschiedene KI-Anbieter (z.B. Anthropic Claude, Scaleway AI) senden können. Die Plattform
            bietet folgende Hauptfunktionen:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li><strong>KI-Gateway:</strong> Routing von API-Anfragen an verschiedene KI-Provider</li>
            <li><strong>Privacy Shield:</strong> Automatische Erkennung und Entfernung personenbezogener Daten (PII)</li>
            <li><strong>Credit-System:</strong> Prepaid-Abrechnungsmodell mit flexiblem Credit-Management</li>
            <li><strong>Multi-Tenant-Verwaltung:</strong> Für Enterprise-Kunden</li>
            <li><strong>Nutzungsstatistiken:</strong> Detaillierte Analysen und Reporting</li>
          </ul>

          <h3 className="text-xl font-semibold mb-3 mt-6">2.2 Verfügbarkeit</h3>
          <p className="mb-4">
            Der Anbieter strebt eine Verfügbarkeit von 99,5% pro Monat an (gemessen über einen Kalendermonat).
            Ausgenommen sind:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li>Geplante Wartungsarbeiten (angekündigt mit 48h Vorlauf)</li>
            <li>Ausfälle bei Drittanbietern (KI-Provider, Cloud-Hosting)</li>
            <li>Höhere Gewalt</li>
            <li>DDoS-Attacken oder andere externe Angriffe</li>
          </ul>

          <h3 className="text-xl font-semibold mb-3 mt-6">2.3 Leistungsänderungen</h3>
          <p className="mb-4">
            Der Anbieter behält sich vor, die Dienste weiterzuentwickeln und zu ändern, sofern dies
            dem Nutzer zumutbar ist und die Kernfunktionalität erhalten bleibt.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">3. Vertragsschluss und Registrierung</h2>

          <h3 className="text-xl font-semibold mb-3 mt-6">3.1 Registrierung</h3>
          <p className="mb-4">
            Die Nutzung der Dienste erfordert eine Registrierung. Der Nutzer garantiert, dass alle
            Angaben bei der Registrierung wahrheitsgemäß und vollständig sind.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">3.2 Vertragsschluss</h3>
          <p className="mb-4">
            Mit der Registrierung gibt der Nutzer ein verbindliches Angebot zum Abschluss eines
            Nutzungsvertrags ab. Der Anbieter nimmt dieses Angebot durch Freischaltung des Accounts an.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">3.3 Nutzungsberechtigung</h3>
          <p className="mb-4">
            Zur Registrierung berechtigt sind:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li>Natürliche Personen ab 18 Jahren</li>
            <li>Juristische Personen (vertreten durch bevollmächtigte Personen)</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">4. Preise und Zahlung</h2>

          <h3 className="text-xl font-semibold mb-3 mt-6">4.1 Preismodell</h3>
          <p className="mb-4">
            Die Dienste werden über ein <strong>Credit-basiertes Prepaid-System</strong> abgerechnet:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li>1 Credit = 0,01 EUR (zzgl. MwSt.)</li>
            <li>Credits werden vor der Nutzung gekauft</li>
            <li>Pro API-Anfrage werden Credits entsprechend dem gewählten Modell abgezogen</li>
            <li>Aktuelle Preislisten sind unter <Link href="/pricing" className="text-primary hover:underline">/pricing</Link> einsehbar</li>
          </ul>

          <h3 className="text-xl font-semibold mb-3 mt-6">4.2 Zahlungsbedingungen</h3>
          <p className="mb-4">
            Die Zahlung erfolgt ausschließlich per:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li>Kreditkarte (Visa, Mastercard, American Express)</li>
            <li>SEPA-Lastschrift (nur für Geschäftskunden)</li>
            <li>Überweisung (für Enterprise-Verträge)</li>
          </ul>
          <p className="mb-4">
            Die Zahlungsabwicklung erfolgt über <strong>Stripe</strong>. Der Anbieter speichert
            keine Zahlungsdaten.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">4.3 Guthabenverfall</h3>
          <p className="mb-4">
            Gekaufte Credits verfallen nicht und können zeitlich unbegrenzt genutzt werden, solange
            der Account aktiv ist.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">4.4 Preisänderungen</h3>
          <p className="mb-4">
            Der Anbieter behält sich vor, Preise mit einer Ankündigungsfrist von 30 Tagen zu ändern.
            Bereits gekaufte Credits behalten ihre Gültigkeit.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">5. Pflichten des Nutzers</h2>

          <h3 className="text-xl font-semibold mb-3 mt-6">5.1 Zulässige Nutzung</h3>
          <p className="mb-4">
            Der Nutzer verpflichtet sich, die Dienste nur für rechtmäßige Zwecke zu nutzen.
            Unzulässig ist insbesondere:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li>Verstoß gegen geltendes Recht</li>
            <li>Verbreitung von Schadsoftware</li>
            <li>Spam oder unerwünschte Massen-Nachrichten</li>
            <li>Umgehung von technischen Schutzmaßnahmen</li>
            <li>Überlastung der Systeme (außerhalb vereinbarter Limits)</li>
            <li>Erstellung illegaler, diskriminierender oder gewaltverherrlichender Inhalte</li>
          </ul>

          <h3 className="text-xl font-semibold mb-3 mt-6">5.2 Zugangsdaten</h3>
          <p className="mb-4">
            Der Nutzer ist verpflichtet, seine Zugangsdaten (Passwort, API-Keys) geheim zu halten
            und vor unbefugtem Zugriff zu schützen. Bei Verdacht auf Missbrauch ist der Anbieter
            unverzüglich zu informieren.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">5.3 Datenschutz und DSGVO-Compliance</h3>
          <p className="mb-4">
            Bei Verarbeitung personenbezogener Daten über die Plattform ist der Nutzer selbst
            verantwortlich für die Einhaltung der DSGVO. Der Anbieter bietet auf Anfrage einen
            Auftragsverarbeitungsvertrag (AVV) an.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">6. Rechte des Anbieters</h2>

          <h3 className="text-xl font-semibold mb-3 mt-6">6.1 Sperrung und Kündigung</h3>
          <p className="mb-4">
            Der Anbieter kann den Zugang sperren oder den Vertrag außerordentlich kündigen, wenn:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li>Der Nutzer gegen diese AGB verstößt</li>
            <li>Der Nutzer die Dienste missbräuchlich nutzt</li>
            <li>Zahlungen trotz Mahnung nicht erfolgen</li>
            <li>Ein wichtiger Grund vorliegt (z.B. Insolvenz des Nutzers)</li>
          </ul>

          <h3 className="text-xl font-semibold mb-3 mt-6">6.2 Datenverarbeitung</h3>
          <p className="mb-4">
            Der Anbieter ist berechtigt, anonymisierte Nutzungsstatistiken zu erstellen und
            für Produktverbesserungen zu verwenden.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">7. Vertragslaufzeit und Kündigung</h2>

          <h3 className="text-xl font-semibold mb-3 mt-6">7.1 Laufzeit</h3>
          <p className="mb-4">
            Der Vertrag wird auf unbestimmte Zeit geschlossen.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">7.2 Ordentliche Kündigung</h3>
          <p className="mb-4">
            Beide Parteien können den Vertrag jederzeit mit einer Frist von 30 Tagen kündigen.
            Die Kündigung muss schriftlich (E-Mail ausreichend) erfolgen an:
            <a href="mailto:support@ai-orchestra.de" className="text-primary hover:underline ml-1">
              support@ai-orchestra.de
            </a>
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">7.3 Außerordentliche Kündigung</h3>
          <p className="mb-4">
            Das Recht zur außerordentlichen Kündigung aus wichtigem Grund bleibt unberührt.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">7.4 Daten nach Kündigung</h3>
          <p className="mb-4">
            Nach Vertragsende werden alle Nutzerdaten innerhalb von 30 Tagen gelöscht.
            Der Nutzer kann vorher einen Datenexport anfordern. Restguthaben wird nicht erstattet.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">8. Haftung und Gewährleistung</h2>

          <h3 className="text-xl font-semibold mb-3 mt-6">8.1 Haftungsbeschränkung</h3>
          <p className="mb-4">
            Der Anbieter haftet unbeschränkt:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li>Bei Vorsatz und grober Fahrlässigkeit</li>
            <li>Bei Verletzung von Leben, Körper oder Gesundheit</li>
            <li>Nach dem Produkthaftungsgesetz</li>
            <li>Im Rahmen übernommener Garantien</li>
          </ul>
          <p className="mb-4">
            Bei leichter Fahrlässigkeit haftet der Anbieter nur bei Verletzung wesentlicher
            Vertragspflichten (Kardinalpflichten) und beschränkt auf den vertragstypischen,
            vorhersehbaren Schaden.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">8.2 Keine Haftung für Inhalte</h3>
          <p className="mb-4">
            Der Anbieter haftet nicht für Inhalte, die durch KI-Modelle generiert werden.
            Die Verantwortung für generierte Inhalte liegt beim Nutzer.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">8.3 Datenverlust</h3>
          <p className="mb-4">
            Der Anbieter erstellt regelmäßige Backups. Eine Haftung für Datenverlust besteht nur,
            wenn der Nutzer keine eigenen Sicherungen durchgeführt hat und der Verlust bei
            ordnungsgemäßer Datensicherung vermeidbar gewesen wäre.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">9. Datenschutz</h2>
          <p className="mb-4">
            Für die Verarbeitung personenbezogener Daten gilt unsere
            <Link href="/datenschutz" className="text-primary hover:underline ml-1">
              Datenschutzerklärung
            </Link>, die integraler Bestandteil dieser AGB ist.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">10. Geistiges Eigentum</h2>

          <h3 className="text-xl font-semibold mb-3 mt-6">10.1 Rechte des Anbieters</h3>
          <p className="mb-4">
            Alle Rechte an der Plattform, einschließlich Software, Dokumentation und Design,
            verbleiben beim Anbieter. Dem Nutzer wird ein nicht-exklusives, nicht übertragbares
            Nutzungsrecht für die Vertragsdauer eingeräumt.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">10.2 Rechte an generierten Inhalten</h3>
          <p className="mb-4">
            Der Nutzer behält alle Rechte an Inhalten, die er über die Plattform erstellt oder
            generiert. Der Anbieter erhebt keine Ansprüche an diesen Inhalten.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">11. Vertraulichkeit</h2>
          <p className="mb-4">
            Beide Parteien verpflichten sich, vertrauliche Informationen der anderen Partei
            geheim zu halten und nur für Vertragszwecke zu verwenden. Diese Verpflichtung
            besteht auch nach Vertragsende fort.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">12. Änderungen der AGB</h2>
          <p className="mb-4">
            Der Anbieter behält sich vor, diese AGB zu ändern. Änderungen werden dem Nutzer
            mindestens 30 Tage vor Inkrafttreten per E-Mail mitgeteilt. Widerspricht der Nutzer
            nicht innerhalb dieser Frist, gelten die Änderungen als akzeptiert.
          </p>
          <p className="mb-4">
            Bei wesentlichen Änderungen (z.B. Preiserhöhungen über 10%) hat der Nutzer ein
            Sonderkündigungsrecht.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">13. Schlussbestimmungen</h2>

          <h3 className="text-xl font-semibold mb-3 mt-6">13.1 Anwendbares Recht</h3>
          <p className="mb-4">
            Es gilt das Recht der Bundesrepublik Deutschland unter Ausschluss des
            UN-Kaufrechts (CISG).
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">13.2 Gerichtsstand</h3>
          <p className="mb-4">
            Gerichtsstand für alle Streitigkeiten ist [Ort], sofern der Nutzer Kaufmann,
            juristische Person des öffentlichen Rechts oder öffentlich-rechtliches Sondervermögen ist.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">13.3 Salvatorische Klausel</h3>
          <p className="mb-4">
            Sollten einzelne Bestimmungen dieser AGB unwirksam sein oder werden, berührt dies
            die Wirksamkeit der übrigen Bestimmungen nicht.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">13.4 Schriftform</h3>
          <p className="mb-4">
            Änderungen oder Ergänzungen dieser AGB bedürfen der Schriftform. Dies gilt auch
            für die Änderung dieser Schriftformklausel. E-Mail ist ausreichend.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">14. Kontakt</h2>
          <div className="bg-muted p-6 rounded-lg mb-4">
            <p className="mb-2"><strong>Support:</strong> <a href="mailto:support@ai-orchestra.de" className="text-primary hover:underline">support@ai-orchestra.de</a></p>
            <p className="mb-2"><strong>Legal:</strong> <a href="mailto:legal@ai-orchestra.de" className="text-primary hover:underline">legal@ai-orchestra.de</a></p>
            <p className="mb-2"><strong>Billing:</strong> <a href="mailto:billing@ai-orchestra.de" className="text-primary hover:underline">billing@ai-orchestra.de</a></p>
          </div>
        </section>

        <div className="mt-12 pt-8 border-t border-border">
          <p className="text-sm text-muted-foreground text-center">
            <Link href="/impressum" className="text-primary hover:underline">Impressum</Link>
            {" • "}
            <Link href="/datenschutz" className="text-primary hover:underline">Datenschutzerklärung</Link>
            {" • "}
            <Link href="/" className="text-primary hover:underline">Zurück zur Startseite</Link>
          </p>
        </div>

        <div className="mt-8 p-4 bg-muted/50 rounded-lg text-sm text-muted-foreground">
          <p className="text-center">
            Version 1.0 - Stand: Dezember 2025
          </p>
        </div>
      </div>
    </div>
  );
}
