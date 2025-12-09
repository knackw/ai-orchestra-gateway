"""
Internationalization (i18n) Module for AI Orchestra Gateway.

ADMIN-007: Multi-Language Support for error messages and responses.

Supported languages:
- English (en) - Default
- German (de)
- French (fr)
- Spanish (es)
"""

import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages."""
    EN = "en"
    DE = "de"
    FR = "fr"
    ES = "es"

    @classmethod
    def from_string(cls, value: str) -> "Language":
        """Create Language from string, with fallback to EN."""
        clean = value.lower().split("-")[0]
        for lang in cls:
            if lang.value == clean:
                return lang
        return cls.EN


# Default language
DEFAULT_LANGUAGE = Language.EN


@dataclass
class TranslationConfig:
    """Configuration for translation service."""
    default_language: Language = DEFAULT_LANGUAGE
    fallback_to_default: bool = True
    translations_path: Optional[str] = None


# Built-in translations
TRANSLATIONS: dict[Language, dict[str, str]] = {
    Language.EN: {
        # Auth
        "auth.missing_license_key": "License key is required",
        "auth.invalid_license": "Invalid license key",
        "auth.inactive_license": "License is inactive",
        "auth.expired_license": "License has expired",
        "auth.no_credits": "No credits remaining",
        "auth.ip_not_allowed": "Access from this IP address is not allowed",

        # RBAC
        "rbac.no_access": "You do not have access to this resource",
        "rbac.insufficient_permissions": "Insufficient permissions for this action",
        "rbac.insufficient_role": "Your role does not allow this action",

        # Billing
        "billing.insufficient_credits": "Insufficient credits. Required: {required}, Available: {available}",
        "billing.payment_required": "Payment required to continue",
        "billing.credits_added": "{amount} credits added to your account",

        # Rate Limit
        "rate_limit.exceeded": "Rate limit exceeded. Try again in {seconds} seconds",
        "rate_limit.too_many_requests": "Too many requests. Please slow down",

        # AI
        "ai.provider_unavailable": "AI provider '{provider}' is temporarily unavailable",
        "ai.generation_failed": "AI generation failed: {reason}",
        "ai.all_providers_failed": "All AI providers are currently unavailable",

        # Tenant
        "tenant.not_found": "Tenant not found",
        "tenant.inactive": "Tenant account is inactive",
        "tenant.deletion_not_allowed": "Tenant deletion is not allowed",

        # Validation
        "validation.invalid_email": "Invalid email format",
        "validation.required_field": "Field '{field}' is required",
        "validation.invalid_format": "Invalid format for field '{field}'",
        "validation.prompt_too_long": "Prompt exceeds maximum length of {max} characters",

        # Success
        "success.created": "{resource} created successfully",
        "success.updated": "{resource} updated successfully",
        "success.deleted": "{resource} deleted successfully",

        # Errors
        "error.internal": "Internal server error. Please try again later",
        "error.not_found": "Resource not found",
        "error.bad_request": "Bad request: {reason}",
    },
    Language.DE: {
        # Auth
        "auth.missing_license_key": "Lizenzschlüssel ist erforderlich",
        "auth.invalid_license": "Ungültiger Lizenzschlüssel",
        "auth.inactive_license": "Lizenz ist inaktiv",
        "auth.expired_license": "Lizenz ist abgelaufen",
        "auth.no_credits": "Keine Credits mehr verfügbar",
        "auth.ip_not_allowed": "Zugriff von dieser IP-Adresse ist nicht erlaubt",

        # RBAC
        "rbac.no_access": "Sie haben keinen Zugriff auf diese Ressource",
        "rbac.insufficient_permissions": "Unzureichende Berechtigungen für diese Aktion",
        "rbac.insufficient_role": "Ihre Rolle erlaubt diese Aktion nicht",

        # Billing
        "billing.insufficient_credits": "Unzureichende Credits. Benötigt: {required}, Verfügbar: {available}",
        "billing.payment_required": "Zahlung erforderlich um fortzufahren",
        "billing.credits_added": "{amount} Credits wurden Ihrem Konto hinzugefügt",

        # Rate Limit
        "rate_limit.exceeded": "Ratenlimit überschritten. Versuchen Sie es in {seconds} Sekunden erneut",
        "rate_limit.too_many_requests": "Zu viele Anfragen. Bitte verlangsamen",

        # AI
        "ai.provider_unavailable": "KI-Anbieter '{provider}' ist vorübergehend nicht verfügbar",
        "ai.generation_failed": "KI-Generierung fehlgeschlagen: {reason}",
        "ai.all_providers_failed": "Alle KI-Anbieter sind derzeit nicht verfügbar",

        # Tenant
        "tenant.not_found": "Mandant nicht gefunden",
        "tenant.inactive": "Mandantenkonto ist inaktiv",
        "tenant.deletion_not_allowed": "Löschung des Mandanten ist nicht erlaubt",

        # Validation
        "validation.invalid_email": "Ungültiges E-Mail-Format",
        "validation.required_field": "Feld '{field}' ist erforderlich",
        "validation.invalid_format": "Ungültiges Format für Feld '{field}'",
        "validation.prompt_too_long": "Prompt überschreitet maximale Länge von {max} Zeichen",

        # Success
        "success.created": "{resource} erfolgreich erstellt",
        "success.updated": "{resource} erfolgreich aktualisiert",
        "success.deleted": "{resource} erfolgreich gelöscht",

        # Errors
        "error.internal": "Interner Serverfehler. Bitte versuchen Sie es später erneut",
        "error.not_found": "Ressource nicht gefunden",
        "error.bad_request": "Ungültige Anfrage: {reason}",
    },
    Language.FR: {
        # Auth
        "auth.missing_license_key": "La clé de licence est requise",
        "auth.invalid_license": "Clé de licence invalide",
        "auth.inactive_license": "La licence est inactive",
        "auth.expired_license": "La licence a expiré",
        "auth.no_credits": "Plus de crédits disponibles",
        "auth.ip_not_allowed": "L'accès depuis cette adresse IP n'est pas autorisé",

        # RBAC
        "rbac.no_access": "Vous n'avez pas accès à cette ressource",
        "rbac.insufficient_permissions": "Permissions insuffisantes pour cette action",
        "rbac.insufficient_role": "Votre rôle ne permet pas cette action",

        # Billing
        "billing.insufficient_credits": "Crédits insuffisants. Requis: {required}, Disponible: {available}",
        "billing.payment_required": "Paiement requis pour continuer",
        "billing.credits_added": "{amount} crédits ajoutés à votre compte",

        # Rate Limit
        "rate_limit.exceeded": "Limite de débit dépassée. Réessayez dans {seconds} secondes",
        "rate_limit.too_many_requests": "Trop de requêtes. Veuillez ralentir",

        # AI
        "ai.provider_unavailable": "Le fournisseur IA '{provider}' est temporairement indisponible",
        "ai.generation_failed": "La génération IA a échoué: {reason}",
        "ai.all_providers_failed": "Tous les fournisseurs IA sont actuellement indisponibles",

        # Tenant
        "tenant.not_found": "Locataire non trouvé",
        "tenant.inactive": "Le compte du locataire est inactif",
        "tenant.deletion_not_allowed": "La suppression du locataire n'est pas autorisée",

        # Validation
        "validation.invalid_email": "Format d'email invalide",
        "validation.required_field": "Le champ '{field}' est requis",
        "validation.invalid_format": "Format invalide pour le champ '{field}'",
        "validation.prompt_too_long": "Le prompt dépasse la longueur maximale de {max} caractères",

        # Success
        "success.created": "{resource} créé avec succès",
        "success.updated": "{resource} mis à jour avec succès",
        "success.deleted": "{resource} supprimé avec succès",

        # Errors
        "error.internal": "Erreur serveur interne. Veuillez réessayer plus tard",
        "error.not_found": "Ressource non trouvée",
        "error.bad_request": "Requête invalide: {reason}",
    },
    Language.ES: {
        # Auth
        "auth.missing_license_key": "Se requiere la clave de licencia",
        "auth.invalid_license": "Clave de licencia inválida",
        "auth.inactive_license": "La licencia está inactiva",
        "auth.expired_license": "La licencia ha expirado",
        "auth.no_credits": "No quedan créditos",
        "auth.ip_not_allowed": "El acceso desde esta dirección IP no está permitido",

        # RBAC
        "rbac.no_access": "No tiene acceso a este recurso",
        "rbac.insufficient_permissions": "Permisos insuficientes para esta acción",
        "rbac.insufficient_role": "Su rol no permite esta acción",

        # Billing
        "billing.insufficient_credits": "Créditos insuficientes. Requerido: {required}, Disponible: {available}",
        "billing.payment_required": "Se requiere pago para continuar",
        "billing.credits_added": "{amount} créditos agregados a su cuenta",

        # Rate Limit
        "rate_limit.exceeded": "Límite de tasa excedido. Intente de nuevo en {seconds} segundos",
        "rate_limit.too_many_requests": "Demasiadas solicitudes. Por favor reduzca la velocidad",

        # AI
        "ai.provider_unavailable": "El proveedor de IA '{provider}' está temporalmente no disponible",
        "ai.generation_failed": "La generación de IA falló: {reason}",
        "ai.all_providers_failed": "Todos los proveedores de IA están actualmente no disponibles",

        # Tenant
        "tenant.not_found": "Inquilino no encontrado",
        "tenant.inactive": "La cuenta del inquilino está inactiva",
        "tenant.deletion_not_allowed": "No se permite la eliminación del inquilino",

        # Validation
        "validation.invalid_email": "Formato de email inválido",
        "validation.required_field": "El campo '{field}' es requerido",
        "validation.invalid_format": "Formato inválido para el campo '{field}'",
        "validation.prompt_too_long": "El prompt excede la longitud máxima de {max} caracteres",

        # Success
        "success.created": "{resource} creado exitosamente",
        "success.updated": "{resource} actualizado exitosamente",
        "success.deleted": "{resource} eliminado exitosamente",

        # Errors
        "error.internal": "Error interno del servidor. Por favor intente más tarde",
        "error.not_found": "Recurso no encontrado",
        "error.bad_request": "Solicitud inválida: {reason}",
    },
}


class I18nService:
    """
    Internationalization service for translating messages.

    Usage:
        i18n = I18nService()
        message = i18n.get("error.unauthorized", Language.DE)
    """

    def __init__(self, config: Optional[TranslationConfig] = None):
        """
        Initialize i18n service.

        Args:
            config: Translation configuration
        """
        self.config = config or TranslationConfig()
        self._translations: dict[Language, dict[str, str]] = {
            lang: trans.copy() for lang, trans in TRANSLATIONS.items()
        }
        self._load_custom_translations()

    def _load_custom_translations(self) -> None:
        """Load custom translations from file if configured."""
        if self.config.translations_path:
            try:
                path = Path(self.config.translations_path)
                if path.exists():
                    with open(path, "r", encoding="utf-8") as f:
                        custom = json.load(f)
                        for lang_str, translations in custom.items():
                            lang = Language.from_string(lang_str)
                            if lang not in self._translations:
                                self._translations[lang] = {}
                            self._translations[lang].update(translations)
                    logger.info(f"Loaded custom translations from {path}")
            except Exception as e:
                logger.error(f"Failed to load custom translations: {e}")

    def get(
        self,
        key: str,
        language: Optional[Language | str] = None,
        **kwargs,
    ) -> str:
        """
        Get translated message.

        Args:
            key: Translation key (e.g., "error.unauthorized")
            language: Language (enum or string), defaults to config default
            **kwargs: Interpolation values

        Returns:
            Translated string
        """
        # Resolve language
        if language is None:
            lang = self.config.default_language
        elif isinstance(language, str):
            lang = Language.from_string(language)
        else:
            lang = language

        # Try requested language
        if lang in self._translations and key in self._translations[lang]:
            return self._interpolate(self._translations[lang][key], kwargs)

        # Fallback to default language
        if self.config.fallback_to_default and lang != self.config.default_language:
            default = self.config.default_language
            if default in self._translations and key in self._translations[default]:
                return self._interpolate(self._translations[default][key], kwargs)

        # Return key if no translation found
        logger.warning(f"Missing translation for key: {key}")
        return key

    def _interpolate(self, message: str, values: dict) -> str:
        """Interpolate values into message string."""
        if not values:
            return message
        try:
            return message.format(**values)
        except KeyError as e:
            logger.warning(f"Missing interpolation value: {e}")
            return message

    def has_key(self, key: str) -> bool:
        """Check if translation key exists."""
        for translations in self._translations.values():
            if key in translations:
                return True
        return False

    def add_translation(
        self,
        key: str,
        translations: dict[Language | str, str],
    ) -> None:
        """
        Add or update a translation.

        Args:
            key: Translation key
            translations: Dict mapping language to translation
        """
        for lang, text in translations.items():
            if isinstance(lang, str):
                lang = Language.from_string(lang)
            if lang not in self._translations:
                self._translations[lang] = {}
            self._translations[lang][key] = text

    def get_available_languages(self) -> list[Language]:
        """Get list of available languages."""
        return list(Language)


class I18nContext:
    """Context for translations with a fixed language."""

    def __init__(self, language: Optional[Language] = None):
        """Initialize context with language."""
        self.language = language or DEFAULT_LANGUAGE
        self._service = get_i18n_service()

    def t(self, key: str, **kwargs) -> str:
        """Translate with context language."""
        return self._service.get(key, self.language, **kwargs)


def get_accept_language(header: Optional[str]) -> Language:
    """
    Parse Accept-Language header and return best matching language.

    Args:
        header: Accept-Language header value

    Returns:
        Best matching Language
    """
    if not header:
        return DEFAULT_LANGUAGE

    # Parse Accept-Language header
    # Format: de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7
    languages_with_quality: list[tuple[str, float]] = []

    for part in header.split(","):
        part = part.strip()
        if ";q=" in part:
            lang, q = part.split(";q=")
            try:
                quality = float(q)
            except ValueError:
                quality = 1.0
        else:
            lang = part
            quality = 1.0

        # Extract base language code
        base_lang = lang.split("-")[0].lower()
        languages_with_quality.append((base_lang, quality))

    # Sort by quality descending
    languages_with_quality.sort(key=lambda x: x[1], reverse=True)

    # Find first supported language
    for lang_code, _ in languages_with_quality:
        try:
            return Language(lang_code)
        except ValueError:
            continue

    return DEFAULT_LANGUAGE


async def get_request_language(request) -> Language:
    """
    Detect language from request (query param > header > default).

    Args:
        request: FastAPI request object

    Returns:
        Detected Language
    """
    # Check query parameter first
    lang_param = request.query_params.get("lang")
    if lang_param:
        try:
            return Language(lang_param.lower())
        except ValueError:
            pass

    # Check Accept-Language header
    accept_lang = request.headers.get("Accept-Language")
    if accept_lang:
        return get_accept_language(accept_lang)

    return DEFAULT_LANGUAGE


# Global i18n service instance
_i18n_service: Optional[I18nService] = None


def get_i18n_service() -> I18nService:
    """
    Get or create the global i18n service.

    Returns:
        I18nService instance
    """
    global _i18n_service
    if _i18n_service is None:
        _i18n_service = I18nService()
    return _i18n_service


def t(key: str, language: str | Language = DEFAULT_LANGUAGE, **kwargs) -> str:
    """
    Shorthand for translating a key.

    Args:
        key: Translation key
        language: Language code or enum
        **kwargs: Interpolation values

    Returns:
        Translated string
    """
    return get_i18n_service().get(key, language, **kwargs)


# Export all
__all__ = [
    "Language",
    "I18nService",
    "I18nContext",
    "TranslationConfig",
    "DEFAULT_LANGUAGE",
    "get_i18n_service",
    "get_accept_language",
    "get_request_language",
    "t",
]
