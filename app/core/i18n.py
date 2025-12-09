"""
Internationalization (i18n) Service for AI Gateway.

Provides multi-language support for:
- API error messages
- Email templates
- User-facing content
"""

import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from fastapi import Header, Request

logger = logging.getLogger(__name__)


class Language(str, Enum):
    """Supported languages."""
    EN = "en"
    DE = "de"
    FR = "fr"
    ES = "es"


DEFAULT_LANGUAGE = Language.EN

# Translation storage
_translations: dict[str, dict[str, str]] = {}


@dataclass
class TranslationConfig:
    """Configuration for translation service."""
    default_language: Language = Language.EN
    fallback_to_default: bool = True
    translations_path: str | None = None


def _load_embedded_translations() -> dict[str, dict[str, str]]:
    """Load embedded translations for API messages."""
    return {
        # Authentication errors
        "auth.missing_license_key": {
            Language.EN: "Missing X-License-Key header",
            Language.DE: "X-License-Key Header fehlt",
            Language.FR: "En-tête X-License-Key manquant",
            Language.ES: "Falta el encabezado X-License-Key",
        },
        "auth.invalid_license": {
            Language.EN: "Invalid license key",
            Language.DE: "Ungültiger Lizenzschlüssel",
            Language.FR: "Clé de licence invalide",
            Language.ES: "Clave de licencia inválida",
        },
        "auth.inactive_license": {
            Language.EN: "License is not active",
            Language.DE: "Lizenz ist nicht aktiv",
            Language.FR: "La licence n'est pas active",
            Language.ES: "La licencia no está activa",
        },
        "auth.expired_license": {
            Language.EN: "License has expired",
            Language.DE: "Lizenz ist abgelaufen",
            Language.FR: "La licence a expiré",
            Language.ES: "La licencia ha caducado",
        },
        "auth.no_credits": {
            Language.EN: "No credits remaining. Please purchase more credits.",
            Language.DE: "Keine Credits mehr vorhanden. Bitte erwerben Sie weitere Credits.",
            Language.FR: "Plus de crédits disponibles. Veuillez acheter plus de crédits.",
            Language.ES: "No quedan créditos. Por favor, compre más créditos.",
        },
        "auth.ip_not_allowed": {
            Language.EN: "Your IP address is not authorized for this tenant.",
            Language.DE: "Ihre IP-Adresse ist für diesen Mandanten nicht autorisiert.",
            Language.FR: "Votre adresse IP n'est pas autorisée pour ce locataire.",
            Language.ES: "Su dirección IP no está autorizada para este inquilino.",
        },

        # RBAC errors
        "rbac.no_access": {
            Language.EN: "You do not have access to this tenant",
            Language.DE: "Sie haben keinen Zugriff auf diesen Mandanten",
            Language.FR: "Vous n'avez pas accès à ce locataire",
            Language.ES: "No tiene acceso a este inquilino",
        },
        "rbac.insufficient_permissions": {
            Language.EN: "Insufficient permissions",
            Language.DE: "Unzureichende Berechtigungen",
            Language.FR: "Autorisations insuffisantes",
            Language.ES: "Permisos insuficientes",
        },
        "rbac.insufficient_role": {
            Language.EN: "Insufficient role. Required: {role} or higher",
            Language.DE: "Unzureichende Rolle. Erforderlich: {role} oder höher",
            Language.FR: "Rôle insuffisant. Requis: {role} ou supérieur",
            Language.ES: "Rol insuficiente. Requerido: {role} o superior",
        },

        # Billing errors
        "billing.insufficient_credits": {
            Language.EN: "Insufficient credits. Required: {required}, Available: {available}",
            Language.DE: "Unzureichende Credits. Benötigt: {required}, Verfügbar: {available}",
            Language.FR: "Crédits insuffisants. Requis: {required}, Disponible: {available}",
            Language.ES: "Créditos insuficientes. Requeridos: {required}, Disponibles: {available}",
        },
        "billing.payment_required": {
            Language.EN: "Payment required. Please add credits to continue.",
            Language.DE: "Zahlung erforderlich. Bitte fügen Sie Credits hinzu, um fortzufahren.",
            Language.FR: "Paiement requis. Veuillez ajouter des crédits pour continuer.",
            Language.ES: "Pago requerido. Por favor, agregue créditos para continuar.",
        },

        # Rate limiting
        "rate_limit.exceeded": {
            Language.EN: "Rate limit exceeded. Please try again later.",
            Language.DE: "Ratenlimit überschritten. Bitte versuchen Sie es später erneut.",
            Language.FR: "Limite de taux dépassée. Veuillez réessayer plus tard.",
            Language.ES: "Límite de velocidad excedido. Por favor, inténtelo más tarde.",
        },
        "rate_limit.too_many_requests": {
            Language.EN: "Too many requests. Please slow down.",
            Language.DE: "Zu viele Anfragen. Bitte verlangsamen Sie.",
            Language.FR: "Trop de requêtes. Veuillez ralentir.",
            Language.ES: "Demasiadas solicitudes. Por favor, reduzca la velocidad.",
        },

        # AI Provider errors
        "ai.provider_unavailable": {
            Language.EN: "AI provider is temporarily unavailable",
            Language.DE: "KI-Anbieter ist vorübergehend nicht verfügbar",
            Language.FR: "Le fournisseur d'IA est temporairement indisponible",
            Language.ES: "El proveedor de IA no está disponible temporalmente",
        },
        "ai.generation_failed": {
            Language.EN: "Failed to generate response. Please try again.",
            Language.DE: "Antwortgenerierung fehlgeschlagen. Bitte versuchen Sie es erneut.",
            Language.FR: "Échec de la génération de réponse. Veuillez réessayer.",
            Language.ES: "Error al generar respuesta. Por favor, inténtelo de nuevo.",
        },
        "ai.all_providers_failed": {
            Language.EN: "All AI providers are currently unavailable",
            Language.DE: "Alle KI-Anbieter sind derzeit nicht verfügbar",
            Language.FR: "Tous les fournisseurs d'IA sont actuellement indisponibles",
            Language.ES: "Todos los proveedores de IA no están disponibles actualmente",
        },

        # Tenant errors
        "tenant.not_found": {
            Language.EN: "Tenant not found",
            Language.DE: "Mandant nicht gefunden",
            Language.FR: "Locataire non trouvé",
            Language.ES: "Inquilino no encontrado",
        },
        "tenant.inactive": {
            Language.EN: "Tenant is inactive",
            Language.DE: "Mandant ist inaktiv",
            Language.FR: "Le locataire est inactif",
            Language.ES: "El inquilino está inactivo",
        },
        "tenant.deletion_not_allowed": {
            Language.EN: "Only the owner can delete this tenant",
            Language.DE: "Nur der Eigentümer kann diesen Mandanten löschen",
            Language.FR: "Seul le propriétaire peut supprimer ce locataire",
            Language.ES: "Solo el propietario puede eliminar este inquilino",
        },

        # App errors
        "app.not_found": {
            Language.EN: "Application not found",
            Language.DE: "Anwendung nicht gefunden",
            Language.FR: "Application non trouvée",
            Language.ES: "Aplicación no encontrada",
        },
        "app.name_exists": {
            Language.EN: "An application with this name already exists",
            Language.DE: "Eine Anwendung mit diesem Namen existiert bereits",
            Language.FR: "Une application avec ce nom existe déjà",
            Language.ES: "Ya existe una aplicación con este nombre",
        },

        # Validation errors
        "validation.invalid_email": {
            Language.EN: "Invalid email address",
            Language.DE: "Ungültige E-Mail-Adresse",
            Language.FR: "Adresse e-mail invalide",
            Language.ES: "Dirección de correo electrónico inválida",
        },
        "validation.required_field": {
            Language.EN: "{field} is required",
            Language.DE: "{field} ist erforderlich",
            Language.FR: "{field} est requis",
            Language.ES: "{field} es obligatorio",
        },
        "validation.invalid_format": {
            Language.EN: "Invalid format for {field}",
            Language.DE: "Ungültiges Format für {field}",
            Language.FR: "Format invalide pour {field}",
            Language.ES: "Formato inválido para {field}",
        },

        # Success messages
        "success.created": {
            Language.EN: "{resource} created successfully",
            Language.DE: "{resource} erfolgreich erstellt",
            Language.FR: "{resource} créé avec succès",
            Language.ES: "{resource} creado exitosamente",
        },
        "success.updated": {
            Language.EN: "{resource} updated successfully",
            Language.DE: "{resource} erfolgreich aktualisiert",
            Language.FR: "{resource} mis à jour avec succès",
            Language.ES: "{resource} actualizado exitosamente",
        },
        "success.deleted": {
            Language.EN: "{resource} deleted successfully",
            Language.DE: "{resource} erfolgreich gelöscht",
            Language.FR: "{resource} supprimé avec succès",
            Language.ES: "{resource} eliminado exitosamente",
        },

        # General errors
        "error.internal": {
            Language.EN: "An internal error occurred. Please try again later.",
            Language.DE: "Ein interner Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.",
            Language.FR: "Une erreur interne s'est produite. Veuillez réessayer plus tard.",
            Language.ES: "Se produjo un error interno. Por favor, inténtelo más tarde.",
        },
        "error.not_found": {
            Language.EN: "Resource not found",
            Language.DE: "Ressource nicht gefunden",
            Language.FR: "Ressource non trouvée",
            Language.ES: "Recurso no encontrado",
        },
        "error.bad_request": {
            Language.EN: "Invalid request",
            Language.DE: "Ungültige Anfrage",
            Language.FR: "Requête invalide",
            Language.ES: "Solicitud inválida",
        },
    }


class I18nService:
    """
    Internationalization service for multi-language support.

    Features:
    - Translation lookup by key
    - Language detection from headers
    - Fallback to default language
    - Parameter interpolation
    """

    def __init__(self, config: TranslationConfig | None = None):
        """
        Initialize i18n service.

        Args:
            config: Translation configuration
        """
        self.config = config or TranslationConfig()
        self._translations = _load_embedded_translations()
        self._load_custom_translations()

    def _load_custom_translations(self) -> None:
        """Load custom translations from file if configured."""
        if self.config.translations_path:
            path = Path(self.config.translations_path)
            if path.exists():
                try:
                    with open(path) as f:
                        custom = json.load(f)
                        # Merge custom translations
                        for key, translations in custom.items():
                            if key not in self._translations:
                                self._translations[key] = {}
                            self._translations[key].update(translations)
                    logger.info(f"Loaded custom translations from {path}")
                except Exception as e:
                    logger.warning(f"Failed to load custom translations: {e}")

    def get(
        self,
        key: str,
        lang: Language | str | None = None,
        **kwargs,
    ) -> str:
        """
        Get translated text for a key.

        Args:
            key: Translation key (e.g., "auth.invalid_license")
            lang: Target language (defaults to configured default)
            **kwargs: Parameters for interpolation

        Returns:
            Translated string with parameters interpolated
        """
        # Normalize language
        if isinstance(lang, str):
            try:
                lang = Language(lang.lower())
            except ValueError:
                lang = self.config.default_language
        elif lang is None:
            lang = self.config.default_language

        # Look up translation
        translations = self._translations.get(key)
        if not translations:
            logger.warning(f"Translation key not found: {key}")
            return key

        # Get translation for language
        text = translations.get(lang)

        # Fallback to default language
        if text is None and self.config.fallback_to_default:
            text = translations.get(self.config.default_language)

        if text is None:
            logger.warning(f"No translation for key '{key}' in language '{lang}'")
            return key

        # Interpolate parameters
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing parameter for translation '{key}': {e}")

        return text

    def has_key(self, key: str) -> bool:
        """Check if translation key exists."""
        return key in self._translations

    def get_available_languages(self) -> list[Language]:
        """Get list of supported languages."""
        return list(Language)

    def add_translation(
        self,
        key: str,
        translations: dict[Language | str, str],
    ) -> None:
        """
        Add or update translations for a key.

        Args:
            key: Translation key
            translations: Dict mapping language to translation
        """
        if key not in self._translations:
            self._translations[key] = {}

        for lang, text in translations.items():
            if isinstance(lang, str):
                try:
                    lang = Language(lang.lower())
                except ValueError:
                    continue
            self._translations[key][lang] = text


# Global i18n service instance
_i18n_service: I18nService | None = None


def get_i18n_service() -> I18nService:
    """Get the global i18n service instance."""
    global _i18n_service
    if _i18n_service is None:
        _i18n_service = I18nService()
    return _i18n_service


def configure_i18n(config: TranslationConfig) -> I18nService:
    """Configure and return the global i18n service."""
    global _i18n_service
    _i18n_service = I18nService(config=config)
    return _i18n_service


# Translation helper function
def t(key: str, lang: Language | str | None = None, **kwargs) -> str:
    """
    Shorthand for getting translations.

    Args:
        key: Translation key
        lang: Target language
        **kwargs: Parameters for interpolation

    Returns:
        Translated string

    Example:
        >>> t("auth.no_credits", "de")
        "Keine Credits mehr vorhanden..."
    """
    return get_i18n_service().get(key, lang, **kwargs)


# FastAPI Dependencies

def get_accept_language(
    accept_language: str | None = Header(None, alias="Accept-Language"),
) -> Language:
    """
    FastAPI dependency to detect language from Accept-Language header.

    Parses Accept-Language header and returns best matching supported language.

    Example headers:
    - "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
    - "en"
    - "fr-FR"
    """
    if not accept_language:
        return DEFAULT_LANGUAGE

    # Parse Accept-Language header
    languages = []
    for lang_part in accept_language.split(","):
        parts = lang_part.strip().split(";")
        lang = parts[0].strip().lower()

        # Extract quality factor
        quality = 1.0
        for part in parts[1:]:
            if part.strip().startswith("q="):
                try:
                    quality = float(part.strip()[2:])
                except ValueError:
                    pass

        languages.append((lang, quality))

    # Sort by quality
    languages.sort(key=lambda x: x[1], reverse=True)

    # Find best matching supported language
    for lang, _ in languages:
        # Try exact match
        lang_code = lang.split("-")[0]
        try:
            return Language(lang_code)
        except ValueError:
            continue

    return DEFAULT_LANGUAGE


async def get_request_language(request: Request) -> Language:
    """
    Get language from request.

    Checks in order:
    1. Query parameter ?lang=
    2. Accept-Language header
    3. Default language
    """
    # Check query parameter
    lang_param = request.query_params.get("lang")
    if lang_param:
        try:
            return Language(lang_param.lower())
        except ValueError:
            pass

    # Check Accept-Language header
    accept_language = request.headers.get("Accept-Language")
    if accept_language:
        return get_accept_language(accept_language)

    return DEFAULT_LANGUAGE


# Translation middleware context
class I18nContext:
    """Context holder for current request language."""

    def __init__(self, language: Language = DEFAULT_LANGUAGE):
        self.language = language

    def t(self, key: str, **kwargs) -> str:
        """Get translation for current context language."""
        return t(key, self.language, **kwargs)
