"""
Legal documents API endpoints.

Provides endpoints for:
- AGB (Terms of Service)
- Datenschutz (Privacy Policy)
- AVV (Data Processing Agreement / Auftragsverarbeitungsvertrag)
- Impressum (Legal Notice)

All documents are GDPR/DSGVO compliant and version-controlled.

Version: 0.6.1 (GDPR-002)
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field, ConfigDict

from app.core.gdpr import GDPRComplianceChecker, DataProcessingInfo

router = APIRouter()


class LegalDocument(BaseModel):
    """Legal document model."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Datenschutzerklärung",
                "version": "1.0",
                "effective_date": "2025-01-01",
                "content": "# Datenschutzerklärung\n\n...",
                "language": "de",
            }
        }
    )

    title: str = Field(..., description="Document title")
    version: str = Field(..., description="Document version (e.g., 1.0)")
    effective_date: date = Field(..., description="Effective date of this version")
    content: str = Field(..., description="Document content in Markdown format")
    language: str = Field(default="de", description="Document language (de/en)")


class AVVDocument(BaseModel):
    """
    Auftragsverarbeitungsvertrag (Data Processing Agreement).

    Required under GDPR Article 28 for SaaS providers.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Auftragsverarbeitungsvertrag",
                "version": "1.0",
                "effective_date": "2025-01-01",
                "content": "# Auftragsverarbeitungsvertrag\n\n...",
                "language": "de",
                "processors": [],
            }
        }
    )

    title: str = Field(..., description="AVV title")
    version: str = Field(..., description="AVV version")
    effective_date: date = Field(..., description="Effective date")
    content: str = Field(..., description="AVV content in Markdown format")
    language: str = Field(default="de", description="Language (de/en)")

    # Metadata about data processors
    processors: list[DataProcessingInfo] = Field(
        ..., description="List of data processors used by the service"
    )


@router.get("/agb", response_model=LegalDocument)
async def get_terms_of_service(
    language: str = Query(default="de", pattern="^(de|en)$")
) -> LegalDocument:
    """
    Get Terms of Service (AGB - Allgemeine Geschäftsbedingungen).

    Args:
        language: Document language (de or en)

    Returns:
        Legal document with terms of service
    """
    if language == "de":
        content = """# Allgemeine Geschäftsbedingungen (AGB)

**Version:** 1.0
**Stand:** 01.01.2025

## 1. Geltungsbereich

Diese Allgemeinen Geschäftsbedingungen (AGB) gelten für die Nutzung des AI Legal Ops Gateway
(nachfolgend "Service" genannt), bereitgestellt von [Ihr Unternehmen].

## 2. Vertragsgegenstand

Der Service ermöglicht die Integration von KI-Modellen verschiedener Anbieter in Ihre Anwendungen
mit integriertem Datenschutz (PII-Shield) und Multi-Tenant-Verwaltung.

## 3. Leistungsumfang

- AI-Gateway für mehrere Anbieter (Anthropic, Scaleway, Vertex AI)
- Automatische PII-Erkennung und -Redaktion
- DSGVO-konforme Datenverarbeitung (EU-Provider verfügbar)
- Multi-Tenant-Verwaltung mit Lizenz- und Abrechnungssystem
- API-Zugang mit Rate Limiting

## 4. Preise und Zahlung

Die Preise richten sich nach dem gewählten Tarif und der Nutzung (Token-basiert).
Detaillierte Preisinformationen finden Sie auf unserer Website.

## 5. Datenschutz

Siehe separate Datenschutzerklärung und Auftragsverarbeitungsvertrag (AVV).

## 6. Haftung

[Standard-Haftungsausschlüsse gemäß geltendem Recht]

## 7. Laufzeit und Kündigung

Der Vertrag wird auf unbestimmte Zeit geschlossen und kann mit einer Frist von 30 Tagen
zum Monatsende gekündigt werden.

## 8. Schlussbestimmungen

Es gilt das Recht der Bundesrepublik Deutschland. Gerichtsstand ist [Ihr Standort].
"""
    else:  # English
        content = """# Terms of Service

**Version:** 1.0
**Effective Date:** January 1, 2025

## 1. Scope

These Terms of Service govern your use of the AI Legal Ops Gateway
(the "Service"), provided by [Your Company].

## 2. Service Description

The Service enables integration of AI models from various providers into your applications
with built-in data privacy (PII Shield) and multi-tenant management.

## 3. Service Features

- AI Gateway for multiple providers (Anthropic, Scaleway, Vertex AI)
- Automatic PII detection and redaction
- GDPR-compliant data processing (EU providers available)
- Multi-tenant management with licensing and billing
- API access with rate limiting

## 4. Pricing and Payment

Prices are based on your chosen plan and usage (token-based).
Detailed pricing information is available on our website.

## 5. Privacy

See separate Privacy Policy and Data Processing Agreement (DPA).

## 6. Liability

[Standard liability disclaimers according to applicable law]

## 7. Term and Termination

The contract is concluded for an indefinite period and can be terminated
with 30 days' notice to the end of the month.

## 8. Final Provisions

German law applies. Place of jurisdiction is [Your Location].
"""

    return LegalDocument(
        title="Allgemeine Geschäftsbedingungen"
        if language == "de"
        else "Terms of Service",
        version="1.0",
        effective_date=date(2025, 1, 1),
        content=content,
        language=language,
    )


@router.get("/datenschutz", response_model=LegalDocument)
async def get_privacy_policy(
    language: str = Query(default="de", pattern="^(de|en)$")
) -> LegalDocument:
    """
    Get Privacy Policy (Datenschutzerklärung).

    GDPR-compliant privacy policy explaining data processing.

    Args:
        language: Document language (de or en)

    Returns:
        Legal document with privacy policy
    """
    if language == "de":
        content = """# Datenschutzerklärung

**Version:** 1.0
**Stand:** 01.01.2025

## 1. Verantwortlicher

[Ihr Unternehmen]
[Adresse]
E-Mail: [datenschutz@example.com]

## 2. Erhebung und Verarbeitung personenbezogener Daten

### 2.1 Welche Daten erheben wir?

Bei Nutzung unseres Service verarbeiten wir:
- Authentifizierungsdaten (License Keys, API Keys)
- Nutzungsdaten (API-Anfragen, Token-Verbrauch)
- Eingabedaten (Prompts für KI-Modelle, automatisch bereinigt von PII)
- Technische Daten (IP-Adressen, Request-IDs)

### 2.2 PII-Shield (Datenschutz-Schutzschild)

Unser Service erkennt und entfernt automatisch personenbezogene Daten (PII) aus Ihren Prompts:
- E-Mail-Adressen
- Telefonnummern
- IBAN/Bankdaten
- Weitere Identifikatoren

**Wichtig:** Bereinigte Daten werden nie an externe KI-Anbieter weitergegeben.

## 3. Rechtsgrundlage der Verarbeitung

Die Verarbeitung erfolgt auf Grundlage von:
- Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung)
- Art. 6 Abs. 1 lit. f DSGVO (berechtigte Interessen)

## 4. Weitergabe an Dritte (Auftragsverarbeiter)

Wir nutzen folgende Auftragsverarbeiter:
- **Supabase (PostgreSQL):** Datenbank-Hosting (EU-Region)
- **AI-Provider:** Anthropic (US), Scaleway (FR), Google Vertex AI (DE/EU)

Siehe separate AVV (Auftragsverarbeitungsvertrag) für Details.

## 5. EU-konforme Datenverarbeitung

Sie können ausschließlich EU-Provider nutzen (Parameter `eu_only=true`):
- **Scaleway:** Daten bleiben in Frankreich (Paris)
- **Vertex AI:** Daten bleiben in Deutschland (Frankfurt)

## 6. Speicherdauer

- API-Logs: 90 Tage
- Nutzungsdaten: Für Abrechnungszwecke (gesetzliche Aufbewahrungspflicht)
- Prompts: Werden nicht dauerhaft gespeichert

## 7. Ihre Rechte

Sie haben das Recht auf:
- Auskunft (Art. 15 DSGVO)
- Berichtigung (Art. 16 DSGVO)
- Löschung (Art. 17 DSGVO)
- Einschränkung der Verarbeitung (Art. 18 DSGVO)
- Datenübertragbarkeit (Art. 20 DSGVO)
- Widerspruch (Art. 21 DSGVO)

## 8. Kontakt Datenschutzbeauftragter

E-Mail: [datenschutz@example.com]

## 9. Beschwerderecht

Sie haben das Recht, sich bei einer Aufsichtsbehörde zu beschweren.
"""
    else:  # English
        content = """# Privacy Policy

**Version:** 1.0
**Effective Date:** January 1, 2025

## 1. Data Controller

[Your Company]
[Address]
Email: [privacy@example.com]

## 2. Collection and Processing of Personal Data

### 2.1 What data do we collect?

When using our Service, we process:
- Authentication data (License Keys, API Keys)
- Usage data (API requests, token consumption)
- Input data (prompts for AI models, automatically cleaned of PII)
- Technical data (IP addresses, Request IDs)

### 2.2 PII Shield (Data Privacy Shield)

Our Service automatically detects and removes personal data (PII) from your prompts:
- Email addresses
- Phone numbers
- IBAN/bank details
- Other identifiers

**Important:** Cleaned data is never shared with external AI providers.

## 3. Legal Basis for Processing

Processing is based on:
- Art. 6(1)(b) GDPR (contract performance)
- Art. 6(1)(f) GDPR (legitimate interests)

## 4. Sharing with Third Parties (Processors)

We use the following processors:
- **Supabase (PostgreSQL):** Database hosting (EU region)
- **AI Providers:** Anthropic (US), Scaleway (FR), Google Vertex AI (DE/EU)

See separate DPA (Data Processing Agreement) for details.

## 5. EU-Compliant Data Processing

You can use exclusively EU providers (parameter `eu_only=true`):
- **Scaleway:** Data stays in France (Paris)
- **Vertex AI:** Data stays in Germany (Frankfurt)

## 6. Retention Period

- API logs: 90 days
- Usage data: For billing purposes (legal retention requirements)
- Prompts: Not stored permanently

## 7. Your Rights

You have the right to:
- Access (Art. 15 GDPR)
- Rectification (Art. 16 GDPR)
- Erasure (Art. 17 GDPR)
- Restriction of processing (Art. 18 GDPR)
- Data portability (Art. 20 GDPR)
- Object (Art. 21 GDPR)

## 8. Data Protection Officer Contact

Email: [privacy@example.com]

## 9. Right to Complain

You have the right to lodge a complaint with a supervisory authority.
"""

    return LegalDocument(
        title="Datenschutzerklärung" if language == "de" else "Privacy Policy",
        version="1.0",
        effective_date=date(2025, 1, 1),
        content=content,
        language=language,
    )


@router.get("/avv", response_model=AVVDocument)
async def get_data_processing_agreement(
    language: str = Query(default="de", pattern="^(de|en)$")
) -> AVVDocument:
    """
    Get Data Processing Agreement (AVV - Auftragsverarbeitungsvertrag).

    Required under GDPR Article 28 when processing personal data on behalf of customers.
    Includes complete transparency about all data processors and sub-processors.

    Args:
        language: Document language (de or en)

    Returns:
        AVV document with processor information
    """
    # Get processor information for all providers
    processors = []
    for provider in ["anthropic", "scaleway", "vertex_claude", "vertex_gemini"]:
        try:
            processor_info = GDPRComplianceChecker.get_processing_info(provider)
            processors.append(processor_info)
        except ValueError:
            pass

    if language == "de":
        content = """# Auftragsverarbeitungsvertrag (AVV)

**Version:** 1.0
**Stand:** 01.01.2025

Gemäß Art. 28 DSGVO zwischen:

**Auftraggeber:** [Kunde]
**Auftragnehmer:** [Ihr Unternehmen]

## 1. Gegenstand und Dauer

Der Auftragnehmer verarbeitet im Auftrag des Auftraggebers personenbezogene Daten
zur Bereitstellung des AI Legal Ops Gateway Service.

## 2. Art und Zweck der Verarbeitung

- Verarbeitung von Eingabedaten (Prompts) zur KI-Generierung
- Automatische PII-Erkennung und -Redaktion
- Nutzungsdaten für Abrechnung und Monitoring
- Technische Logs für Fehleranalyse

## 3. Kategorien betroffener Personen

- Endnutzer der Kundenanwendung
- Kunden-Administratoren

## 4. Kategorien personenbezogener Daten

- Authentifizierungsdaten (License Keys)
- Nutzungsdaten (API-Nutzung, Token-Verbrauch)
- Eingabedaten (Prompts, bereinigt von PII)
- Technische Daten (IP-Adressen)

## 5. Technische und organisatorische Maßnahmen (TOM)

### 5.1 Verschlüsselung
- TLS 1.3 für alle API-Verbindungen
- AES-256 Verschlüsselung für gespeicherte Daten

### 5.2 PII-Shield
- Automatische Erkennung und Redaktion von:
  - E-Mail-Adressen
  - Telefonnummern
  - IBAN/Bankdaten

### 5.3 Zugriffskontrolle
- API Key / License Key Authentifizierung
- Row-Level Security (RLS) für Multi-Tenant-Isolation
- Role-Based Access Control (RBAC)

### 5.4 Monitoring und Audit
- Vollständige Audit-Logs
- Compliance-Monitoring
- Sicherheitsupdates

## 6. Sub-Auftragsverarbeiter

Der Auftragnehmer nutzt folgende Sub-Auftragsverarbeiter:

### 6.1 Anthropic (US-basiert, nicht EU-konform)
- **Zweck:** AI-Modell (Claude)
- **Standort:** USA
- **EU-Standard-Vertragsklauseln:** Ja
- **Datenspeicherung:** 30 Tage

### 6.2 Scaleway (EU-konform)
- **Zweck:** AI-Modelle (Llama, Mistral, Qwen)
- **Standort:** Frankreich (Paris)
- **DSGVO-konform:** Ja
- **Datenspeicherung:** Keine

### 6.3 Google Cloud / Vertex AI (EU-konform)
- **Zweck:** AI-Modelle (Claude, Gemini)
- **Standort:** Deutschland (Frankfurt)
- **DSGVO-konform:** Ja
- **Datenspeicherung:** Keine

### 6.4 Supabase
- **Zweck:** Datenbank-Hosting
- **Standort:** EU-Region
- **DSGVO-konform:** Ja

## 7. Rechte und Pflichten des Auftraggebers

Der Auftraggeber kann:
- EU-konforme Provider erzwingen (`eu_only=true`)
- Jederzeit Auskunft über Datenverarbeitung verlangen
- Löschung von Daten verlangen

## 8. Löschung und Herausgabe von Daten

Nach Vertragsende werden alle Daten innerhalb von 30 Tagen gelöscht,
soweit keine gesetzlichen Aufbewahrungspflichten bestehen.

## 9. Weisungsbefugnis

Der Auftraggeber erteilt Weisungen über:
- API-Parameter (`eu_only`, `provider`)
- Tenant-Konfiguration
- Lizenz-Management

## 10. Haftung und Schadensersatz

[Haftungsregelungen gemäß DSGVO Art. 82]

## 11. Kontrollrechte

Der Auftraggeber kann jederzeit:
- Audit-Logs einsehen
- Compliance-Berichte anfordern
- Verarbeitungstätigkeiten prüfen (mit Vorankündigung)
"""
    else:  # English
        content = """# Data Processing Agreement (DPA)

**Version:** 1.0
**Effective Date:** January 1, 2025

According to Art. 28 GDPR between:

**Controller:** [Customer]
**Processor:** [Your Company]

## 1. Subject Matter and Duration

The Processor processes personal data on behalf of the Controller
for the provision of the AI Legal Ops Gateway Service.

## 2. Nature and Purpose of Processing

- Processing of input data (prompts) for AI generation
- Automatic PII detection and redaction
- Usage data for billing and monitoring
- Technical logs for error analysis

## 3. Categories of Data Subjects

- End users of customer application
- Customer administrators

## 4. Categories of Personal Data

- Authentication data (License Keys)
- Usage data (API usage, token consumption)
- Input data (prompts, cleaned of PII)
- Technical data (IP addresses)

## 5. Technical and Organizational Measures (TOMs)

### 5.1 Encryption
- TLS 1.3 for all API connections
- AES-256 encryption for stored data

### 5.2 PII Shield
- Automatic detection and redaction of:
  - Email addresses
  - Phone numbers
  - IBAN/bank details

### 5.3 Access Control
- API Key / License Key authentication
- Row-Level Security (RLS) for multi-tenant isolation
- Role-Based Access Control (RBAC)

### 5.4 Monitoring and Audit
- Complete audit logs
- Compliance monitoring
- Security updates

## 6. Sub-Processors

The Processor uses the following sub-processors:

### 6.1 Anthropic (US-based, not EU-compliant)
- **Purpose:** AI model (Claude)
- **Location:** USA
- **EU Standard Contractual Clauses:** Yes
- **Data retention:** 30 days

### 6.2 Scaleway (EU-compliant)
- **Purpose:** AI models (Llama, Mistral, Qwen)
- **Location:** France (Paris)
- **GDPR-compliant:** Yes
- **Data retention:** None

### 6.3 Google Cloud / Vertex AI (EU-compliant)
- **Purpose:** AI models (Claude, Gemini)
- **Location:** Germany (Frankfurt)
- **GDPR-compliant:** Yes
- **Data retention:** None

### 6.4 Supabase
- **Purpose:** Database hosting
- **Location:** EU region
- **GDPR-compliant:** Yes

## 7. Rights and Obligations of Controller

The Controller can:
- Enforce EU-compliant providers (`eu_only=true`)
- Request information about data processing at any time
- Request deletion of data

## 8. Data Deletion and Return

After contract termination, all data will be deleted within 30 days,
unless legal retention requirements apply.

## 9. Instructions

The Controller gives instructions via:
- API parameters (`eu_only`, `provider`)
- Tenant configuration
- License management

## 10. Liability and Compensation

[Liability provisions according to GDPR Art. 82]

## 11. Audit Rights

The Controller can at any time:
- Review audit logs
- Request compliance reports
- Audit processing activities (with prior notice)
"""

    return AVVDocument(
        title="Auftragsverarbeitungsvertrag"
        if language == "de"
        else "Data Processing Agreement",
        version="1.0",
        effective_date=date(2025, 1, 1),
        content=content,
        language=language,
        processors=processors,
    )


@router.get("/impressum", response_model=LegalDocument)
async def get_legal_notice(
    language: str = Query(default="de", pattern="^(de|en)$")
) -> LegalDocument:
    """
    Get Legal Notice (Impressum).

    Required in Germany under §5 TMG (Telemediengesetz).

    Args:
        language: Document language (de or en)

    Returns:
        Legal document with legal notice
    """
    if language == "de":
        content = """# Impressum

**Angaben gemäß § 5 TMG:**

[Ihr Unternehmen]
[Rechtsform]
[Straße und Hausnummer]
[PLZ und Ort]

**Vertreten durch:**
[Geschäftsführer/Vorstand]

**Kontakt:**
Telefon: [Telefonnummer]
E-Mail: [kontakt@example.com]

**Registereintrag:**
Eingetragen im Handelsregister
Registergericht: [Gericht]
Registernummer: [HRB-Nummer]

**Umsatzsteuer-ID:**
Umsatzsteuer-Identifikationsnummer gemäß §27a UStG:
[USt-IdNr.]

**Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV:**
[Name]
[Adresse]

**EU-Streitschlichtung:**

Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:
https://ec.europa.eu/consumers/odr

Unsere E-Mail-Adresse finden Sie oben im Impressum.

**Verbraucherstreitbeilegung/Universalschlichtungsstelle:**

Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer
Verbraucherschlichtungsstelle teilzunehmen.
"""
    else:  # English
        content = """# Legal Notice

**Information according to § 5 TMG (German Telemedia Act):**

[Your Company]
[Legal form]
[Street and number]
[Postal code and city]

**Represented by:**
[Managing Director/Board]

**Contact:**
Phone: [Phone number]
Email: [contact@example.com]

**Register entry:**
Registered in the Commercial Register
Registration court: [Court]
Registration number: [HRB number]

**VAT ID:**
VAT identification number according to §27a UStG:
[VAT ID]

**Responsible for content according to § 55 Abs. 2 RStV:**
[Name]
[Address]

**EU Dispute Resolution:**

The European Commission provides a platform for online dispute resolution (ODR):
https://ec.europa.eu/consumers/odr

You can find our email address in the legal notice above.

**Consumer Dispute Resolution/Universal Arbitration Board:**

We are not willing or obliged to participate in dispute resolution proceedings
before a consumer arbitration board.
"""

    return LegalDocument(
        title="Impressum" if language == "de" else "Legal Notice",
        version="1.0",
        effective_date=date(2025, 1, 1),
        content=content,
        language=language,
    )


@router.get("/processors", response_model=list[DataProcessingInfo])
async def list_data_processors() -> list[DataProcessingInfo]:
    """
    List all data processors and sub-processors.

    Provides complete transparency about data processing as required by GDPR.
    This endpoint returns detailed information about each AI provider including:
    - Data residency (EU/US/Global)
    - Legal basis for processing
    - Security measures
    - Data subject rights
    - Sub-processors

    Returns:
        List of all data processors with complete GDPR information
    """
    processors = []

    for provider in ["anthropic", "scaleway", "vertex_claude", "vertex_gemini"]:
        try:
            processor_info = GDPRComplianceChecker.get_processing_info(provider)
            processors.append(processor_info)
        except ValueError:
            pass

    return processors
