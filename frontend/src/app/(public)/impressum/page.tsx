import { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Impressum | AI Orchestra Gateway",
  description: "Impressum und Anbieterkennzeichnung der AI Orchestra Gateway Plattform gemäß §5 TMG",
};

export default function ImpressumPage() {
  return (
    <div className="container mx-auto py-12 px-4 max-w-4xl">
      <div className="prose prose-slate dark:prose-invert max-w-none">
        <h1 className="text-4xl font-bold mb-8">Impressum</h1>

        <p className="text-muted-foreground mb-8">
          Angaben gemäß § 5 TMG (Telemediengesetz)
        </p>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Anbieter</h2>
          <div className="bg-muted p-6 rounded-lg mb-4">
            <p className="mb-2"><strong>AI Orchestra Gateway</strong></p>
            <p className="mb-2">[Firmenname / Rechtsform]</p>
            <p className="mb-2">[Straße und Hausnummer]</p>
            <p className="mb-2">[PLZ und Ort]</p>
            <p className="mb-2">[Land]</p>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Kontakt</h2>
          <div className="bg-muted p-6 rounded-lg mb-4">
            <p className="mb-2"><strong>Telefon:</strong> [Telefonnummer]</p>
            <p className="mb-2"><strong>E-Mail:</strong> <a href="mailto:info@ai-orchestra.de" className="text-primary hover:underline">info@ai-orchestra.de</a></p>
            <p className="mb-2"><strong>Website:</strong> <a href="https://ai-orchestra.de" className="text-primary hover:underline">https://ai-orchestra.de</a></p>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Vertretungsberechtigt</h2>
          <div className="bg-muted p-6 rounded-lg mb-4">
            <p className="mb-2"><strong>Geschäftsführer:</strong> [Name]</p>
            <p className="mb-2"><strong>Vertretungsberechtigt:</strong> [Name, Funktion]</p>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Registereintrag</h2>
          <div className="bg-muted p-6 rounded-lg mb-4">
            <p className="mb-2"><strong>Handelsregister:</strong> [Amtsgericht, Registernummer]</p>
            <p className="mb-2"><strong>Registernummer:</strong> [HRB-Nummer]</p>
            <p className="mb-2"><strong>Umsatzsteuer-ID:</strong> [USt-IdNr. gemäß §27a UStG]</p>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Verantwortlich für den Inhalt</h2>
          <p className="mb-4">Verantwortlich nach § 55 Abs. 2 RStV:</p>
          <div className="bg-muted p-6 rounded-lg mb-4">
            <p className="mb-2"><strong>[Name]</strong></p>
            <p className="mb-2">[Adresse wie oben]</p>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Berufshaftpflichtversicherung</h2>
          <div className="bg-muted p-6 rounded-lg mb-4">
            <p className="mb-2"><strong>Versicherer:</strong> [Name der Versicherung]</p>
            <p className="mb-2"><strong>Adresse:</strong> [Adresse des Versicherers]</p>
            <p className="mb-2"><strong>Geltungsbereich:</strong> Deutschland / EU</p>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Streitschlichtung</h2>
          <p className="mb-4">
            Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:
          </p>
          <p className="mb-4">
            <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
              https://ec.europa.eu/consumers/odr/
            </a>
          </p>
          <p className="mb-4">
            Unsere E-Mail-Adresse finden Sie oben im Impressum.
          </p>
          <p className="mb-4">
            <strong>Hinweis gemäß § 36 VSBG:</strong> Wir sind nicht bereit und nicht verpflichtet,
            an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Haftungsausschluss</h2>

          <h3 className="text-xl font-semibold mb-3 mt-6">Haftung für Inhalte</h3>
          <p className="mb-4">
            Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach
            den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als Diensteanbieter
            jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen
            oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen.
          </p>
          <p className="mb-4">
            Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den
            allgemeinen Gesetzen bleiben hiervon unberührt. Eine diesbezügliche Haftung ist jedoch
            erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei
            Bekanntwerden von entsprechenden Rechtsverletzungen werden wir diese Inhalte umgehend entfernen.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">Haftung für Links</h3>
          <p className="mb-4">
            Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen
            Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen.
            Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der
            Seiten verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf
            mögliche Rechtsverstöße überprüft. Rechtswidrige Inhalte waren zum Zeitpunkt der Verlinkung
            nicht erkennbar.
          </p>
          <p className="mb-4">
            Eine permanente inhaltliche Kontrolle der verlinkten Seiten ist jedoch ohne konkrete
            Anhaltspunkte einer Rechtsverletzung nicht zumutbar. Bei Bekanntwerden von Rechtsverletzungen
            werden wir derartige Links umgehend entfernen.
          </p>

          <h3 className="text-xl font-semibold mb-3 mt-6">Urheberrecht</h3>
          <p className="mb-4">
            Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen
            dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art
            der Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung
            des jeweiligen Autors bzw. Erstellers. Downloads und Kopien dieser Seite sind nur für den
            privaten, nicht kommerziellen Gebrauch gestattet.
          </p>
          <p className="mb-4">
            Soweit die Inhalte auf dieser Seite nicht vom Betreiber erstellt wurden, werden die
            Urheberrechte Dritter beachtet. Insbesondere werden Inhalte Dritter als solche gekennzeichnet.
            Sollten Sie trotzdem auf eine Urheberrechtsverletzung aufmerksam werden, bitten wir um einen
            entsprechenden Hinweis. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Inhalte
            umgehend entfernen.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Besondere Nutzungsbedingungen</h2>
          <p className="mb-4">
            Für die Nutzung unserer KI-Gateway-Dienste gelten unsere
            <Link href="/agb" className="text-primary hover:underline ml-1 mr-1">Allgemeinen Geschäftsbedingungen (AGB)</Link>
            sowie die
            <Link href="/datenschutz" className="text-primary hover:underline ml-1">Datenschutzerklärung</Link>.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Bildnachweise</h2>
          <p className="mb-4">
            Auf dieser Website verwendete Bilder stammen aus folgenden Quellen:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li>Eigene Fotografien und Grafiken</li>
            <li>Unsplash (unsplash.com) - Lizenzfrei</li>
            <li>Icons: Lucide React (lucide.dev) - MIT License</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Technische Hinweise</h2>
          <p className="mb-4">
            Diese Website verwendet:
          </p>
          <ul className="list-disc pl-6 mb-4 space-y-2">
            <li><strong>Framework:</strong> Next.js 14 (Vercel Inc.)</li>
            <li><strong>Hosting:</strong> Vercel / AWS (EU-Region)</li>
            <li><strong>Datenbank:</strong> Supabase (EU-Region)</li>
            <li><strong>Analytics:</strong> Keine Third-Party Tracking-Tools</li>
          </ul>
          <p className="mb-4">
            Alle eingesetzten Technologien sind DSGVO-konform konfiguriert.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Kontakt für rechtliche Anfragen</h2>
          <div className="bg-muted p-6 rounded-lg mb-4">
            <p className="mb-2"><strong>E-Mail:</strong> <a href="mailto:legal@ai-orchestra.de" className="text-primary hover:underline">legal@ai-orchestra.de</a></p>
            <p className="mb-2"><strong>Datenschutz:</strong> <a href="mailto:privacy@ai-orchestra.de" className="text-primary hover:underline">privacy@ai-orchestra.de</a></p>
            <p className="mb-2"><strong>Support:</strong> <a href="mailto:support@ai-orchestra.de" className="text-primary hover:underline">support@ai-orchestra.de</a></p>
          </div>
        </section>

        <div className="mt-12 pt-8 border-t border-border">
          <p className="text-sm text-muted-foreground text-center">
            <Link href="/datenschutz" className="text-primary hover:underline">Datenschutzerklärung</Link>
            {" • "}
            <Link href="/agb" className="text-primary hover:underline">AGB</Link>
            {" • "}
            <Link href="/" className="text-primary hover:underline">Zurück zur Startseite</Link>
          </p>
        </div>

        <div className="mt-8 p-4 bg-muted/50 rounded-lg text-sm text-muted-foreground">
          <p className="text-center">
            Letzte Aktualisierung: Dezember 2025
          </p>
        </div>
      </div>
    </div>
  );
}
