"""
Unit tests for Internationalization (i18n) Service.

Tests:
- Translation lookup
- Language detection
- Fallback behavior
- Parameter interpolation
"""

import pytest
from unittest.mock import MagicMock

from app.core.i18n import (
    Language,
    I18nService,
    TranslationConfig,
    get_i18n_service,
    t,
    get_accept_language,
    get_request_language,
    I18nContext,
    DEFAULT_LANGUAGE,
)


class TestLanguageEnum:
    """Tests for Language enum."""

    def test_language_values(self):
        """Language values should match expected codes."""
        assert Language.EN.value == "en"
        assert Language.DE.value == "de"
        assert Language.FR.value == "fr"
        assert Language.ES.value == "es"

    def test_language_from_string(self):
        """Should create Language from string value."""
        assert Language("en") == Language.EN
        assert Language("de") == Language.DE
        assert Language("fr") == Language.FR
        assert Language("es") == Language.ES


class TestI18nService:
    """Tests for I18nService."""

    @pytest.fixture
    def i18n(self):
        """Create i18n service instance."""
        return I18nService()

    def test_get_translation_english(self, i18n):
        """Should return English translation."""
        result = i18n.get("auth.invalid_license", Language.EN)
        assert result == "Invalid license key"

    def test_get_translation_german(self, i18n):
        """Should return German translation."""
        result = i18n.get("auth.invalid_license", Language.DE)
        assert result == "Ungültiger Lizenzschlüssel"

    def test_get_translation_french(self, i18n):
        """Should return French translation."""
        result = i18n.get("auth.invalid_license", Language.FR)
        assert result == "Clé de licence invalide"

    def test_get_translation_spanish(self, i18n):
        """Should return Spanish translation."""
        result = i18n.get("auth.invalid_license", Language.ES)
        assert result == "Clave de licencia inválida"

    def test_get_translation_with_string_language(self, i18n):
        """Should accept language as string."""
        result = i18n.get("auth.invalid_license", "de")
        assert result == "Ungültiger Lizenzschlüssel"

    def test_get_translation_default_language(self, i18n):
        """Should use default language when not specified."""
        result = i18n.get("auth.invalid_license")
        assert result == "Invalid license key"

    def test_get_translation_fallback(self):
        """Should fallback to default language when translation missing."""
        i18n = I18nService(TranslationConfig(fallback_to_default=True))
        # Add a translation without German
        i18n.add_translation("test.key", {Language.EN: "English only"})

        result = i18n.get("test.key", Language.DE)
        assert result == "English only"

    def test_get_translation_key_not_found(self, i18n):
        """Should return key when translation not found."""
        result = i18n.get("nonexistent.key", Language.EN)
        assert result == "nonexistent.key"

    def test_get_translation_with_parameters(self, i18n):
        """Should interpolate parameters."""
        result = i18n.get(
            "billing.insufficient_credits",
            Language.EN,
            required=100,
            available=50,
        )
        assert result == "Insufficient credits. Required: 100, Available: 50"

    def test_get_translation_german_with_parameters(self, i18n):
        """Should interpolate parameters in German."""
        result = i18n.get(
            "billing.insufficient_credits",
            Language.DE,
            required=100,
            available=50,
        )
        assert result == "Unzureichende Credits. Benötigt: 100, Verfügbar: 50"

    def test_get_translation_missing_parameter(self, i18n):
        """Should handle missing parameters gracefully."""
        result = i18n.get(
            "billing.insufficient_credits",
            Language.EN,
            # Missing 'available' parameter
            required=100,
        )
        # Should return partially formatted or original with warning
        assert "required" in result.lower() or "{available}" in result

    def test_has_key_exists(self, i18n):
        """Should return True for existing key."""
        assert i18n.has_key("auth.invalid_license") is True

    def test_has_key_not_exists(self, i18n):
        """Should return False for non-existing key."""
        assert i18n.has_key("nonexistent.key") is False

    def test_get_available_languages(self, i18n):
        """Should return all supported languages."""
        languages = i18n.get_available_languages()
        assert Language.EN in languages
        assert Language.DE in languages
        assert Language.FR in languages
        assert Language.ES in languages

    def test_add_translation(self, i18n):
        """Should add new translation."""
        i18n.add_translation("custom.message", {
            Language.EN: "Custom English",
            Language.DE: "Benutzerdefiniert Deutsch",
        })

        assert i18n.get("custom.message", Language.EN) == "Custom English"
        assert i18n.get("custom.message", Language.DE) == "Benutzerdefiniert Deutsch"

    def test_add_translation_string_keys(self, i18n):
        """Should accept string language keys."""
        i18n.add_translation("string.key.test", {
            "en": "English",
            "de": "Deutsch",
        })

        assert i18n.get("string.key.test", Language.EN) == "English"
        assert i18n.get("string.key.test", Language.DE) == "Deutsch"


class TestTranslationHelper:
    """Tests for t() shorthand function."""

    def test_t_function_english(self):
        """t() should return English translation."""
        result = t("auth.invalid_license", "en")
        assert result == "Invalid license key"

    def test_t_function_german(self):
        """t() should return German translation."""
        result = t("auth.invalid_license", "de")
        assert result == "Ungültiger Lizenzschlüssel"

    def test_t_function_with_parameters(self):
        """t() should interpolate parameters."""
        result = t("success.created", "en", resource="User")
        assert result == "User created successfully"

    def test_t_function_default_language(self):
        """t() should use default language when not specified."""
        result = t("auth.invalid_license")
        assert result == "Invalid license key"


class TestAcceptLanguageParser:
    """Tests for Accept-Language header parsing."""

    def test_simple_language(self):
        """Should parse simple language code."""
        result = get_accept_language("en")
        assert result == Language.EN

    def test_language_with_region(self):
        """Should parse language with region code."""
        result = get_accept_language("de-DE")
        assert result == Language.DE

    def test_multiple_languages(self):
        """Should select highest quality language."""
        result = get_accept_language("de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7")
        assert result == Language.DE

    def test_quality_factor_selection(self):
        """Should respect quality factors."""
        # English has higher quality
        result = get_accept_language("de;q=0.5,en;q=0.9")
        assert result == Language.EN

    def test_unsupported_language_fallback(self):
        """Should fallback to default for unsupported language."""
        result = get_accept_language("ja-JP")  # Japanese not supported
        assert result == DEFAULT_LANGUAGE

    def test_empty_header(self):
        """Should return default for empty header."""
        result = get_accept_language(None)
        assert result == DEFAULT_LANGUAGE

    def test_mixed_supported_unsupported(self):
        """Should skip unsupported languages."""
        # Japanese highest quality but unsupported
        result = get_accept_language("ja;q=1.0,de;q=0.8,en;q=0.5")
        assert result == Language.DE


class TestRequestLanguage:
    """Tests for request language detection."""

    @pytest.mark.asyncio
    async def test_language_from_query_param(self):
        """Should detect language from query parameter."""
        request = MagicMock()
        request.query_params = {"lang": "de"}
        request.headers = {}

        result = await get_request_language(request)
        assert result == Language.DE

    @pytest.mark.asyncio
    async def test_language_from_header(self):
        """Should detect language from Accept-Language header."""
        request = MagicMock()
        request.query_params = {}
        request.headers = {"Accept-Language": "fr-FR"}

        result = await get_request_language(request)
        assert result == Language.FR

    @pytest.mark.asyncio
    async def test_query_param_priority(self):
        """Query param should take priority over header."""
        request = MagicMock()
        request.query_params = {"lang": "es"}
        request.headers = {"Accept-Language": "de-DE"}

        result = await get_request_language(request)
        assert result == Language.ES

    @pytest.mark.asyncio
    async def test_default_when_nothing_specified(self):
        """Should return default when nothing specified."""
        request = MagicMock()
        request.query_params = {}
        request.headers = {}

        result = await get_request_language(request)
        assert result == DEFAULT_LANGUAGE

    @pytest.mark.asyncio
    async def test_invalid_query_param(self):
        """Should fallback when query param is invalid."""
        request = MagicMock()
        request.query_params = {"lang": "invalid"}
        request.headers = {"Accept-Language": "de"}

        result = await get_request_language(request)
        assert result == Language.DE


class TestI18nContext:
    """Tests for I18nContext."""

    def test_context_translation(self):
        """Context should translate with set language."""
        ctx = I18nContext(Language.DE)
        result = ctx.t("auth.invalid_license")
        assert result == "Ungültiger Lizenzschlüssel"

    def test_context_with_parameters(self):
        """Context should interpolate parameters."""
        ctx = I18nContext(Language.DE)
        result = ctx.t("success.created", resource="Benutzer")
        assert result == "Benutzer erfolgreich erstellt"

    def test_context_default_language(self):
        """Context should use default language by default."""
        ctx = I18nContext()
        result = ctx.t("auth.invalid_license")
        assert result == "Invalid license key"


class TestTranslationCategories:
    """Tests for different translation categories."""

    @pytest.fixture
    def i18n(self):
        """Create i18n service instance."""
        return I18nService()

    def test_auth_translations(self, i18n):
        """Auth translations should be available."""
        assert i18n.has_key("auth.missing_license_key")
        assert i18n.has_key("auth.invalid_license")
        assert i18n.has_key("auth.inactive_license")
        assert i18n.has_key("auth.expired_license")
        assert i18n.has_key("auth.no_credits")
        assert i18n.has_key("auth.ip_not_allowed")

    def test_rbac_translations(self, i18n):
        """RBAC translations should be available."""
        assert i18n.has_key("rbac.no_access")
        assert i18n.has_key("rbac.insufficient_permissions")
        assert i18n.has_key("rbac.insufficient_role")

    def test_billing_translations(self, i18n):
        """Billing translations should be available."""
        assert i18n.has_key("billing.insufficient_credits")
        assert i18n.has_key("billing.payment_required")

    def test_rate_limit_translations(self, i18n):
        """Rate limit translations should be available."""
        assert i18n.has_key("rate_limit.exceeded")
        assert i18n.has_key("rate_limit.too_many_requests")

    def test_ai_translations(self, i18n):
        """AI provider translations should be available."""
        assert i18n.has_key("ai.provider_unavailable")
        assert i18n.has_key("ai.generation_failed")
        assert i18n.has_key("ai.all_providers_failed")

    def test_tenant_translations(self, i18n):
        """Tenant translations should be available."""
        assert i18n.has_key("tenant.not_found")
        assert i18n.has_key("tenant.inactive")
        assert i18n.has_key("tenant.deletion_not_allowed")

    def test_validation_translations(self, i18n):
        """Validation translations should be available."""
        assert i18n.has_key("validation.invalid_email")
        assert i18n.has_key("validation.required_field")
        assert i18n.has_key("validation.invalid_format")

    def test_success_translations(self, i18n):
        """Success message translations should be available."""
        assert i18n.has_key("success.created")
        assert i18n.has_key("success.updated")
        assert i18n.has_key("success.deleted")

    def test_error_translations(self, i18n):
        """General error translations should be available."""
        assert i18n.has_key("error.internal")
        assert i18n.has_key("error.not_found")
        assert i18n.has_key("error.bad_request")


class TestTranslationConfig:
    """Tests for TranslationConfig."""

    def test_default_config(self):
        """Default config should have sensible defaults."""
        config = TranslationConfig()
        assert config.default_language == Language.EN
        assert config.fallback_to_default is True
        assert config.translations_path is None

    def test_custom_config(self):
        """Should allow custom configuration."""
        config = TranslationConfig(
            default_language=Language.DE,
            fallback_to_default=False,
            translations_path="/custom/translations.json",
        )
        assert config.default_language == Language.DE
        assert config.fallback_to_default is False
        assert config.translations_path == "/custom/translations.json"

    def test_service_with_custom_default(self):
        """Service should use custom default language."""
        i18n = I18nService(TranslationConfig(default_language=Language.DE))
        result = i18n.get("auth.invalid_license")
        assert result == "Ungültiger Lizenzschlüssel"


class TestGetI18nService:
    """Tests for global i18n service singleton."""

    def test_returns_instance(self):
        """Should return I18nService instance."""
        service = get_i18n_service()
        assert isinstance(service, I18nService)

    def test_singleton(self):
        """Should return same instance on multiple calls."""
        service1 = get_i18n_service()
        service2 = get_i18n_service()
        assert service1 is service2
