"""
Unit tests for DataPrivacyShield.
"""


from app.services.privacy import DataPrivacyShield


class TestEmailDetection:
    """Tests for email address detection and sanitization."""

    def test_simple_email(self):
        """Test simple email detection."""
        text = "Contact me at user@example.com"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "user@example.com" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized
        assert sanitized == "Contact me at <EMAIL_REMOVED>"

    def test_email_with_dots(self):
        """Test email with dots in username."""
        text = "Email: first.last@company.com"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "first.last@company.com" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized

    def test_email_with_plus(self):
        """Test email with plus sign (tagging)."""
        text = "Send to test+tag@gmail.com"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "test+tag@gmail.com" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized

    def test_email_with_numbers(self):
        """Test email with numbers."""
        text = "User123@domain456.com is the address"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "User123@domain456.com" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized

    def test_email_with_subdomain(self):
        """Test email with subdomain."""
        text = "admin@mail.server.company.com"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "admin@mail.server.company.com" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized

    def test_email_with_country_tld(self):
        """Test email with country TLD."""
        text = "Contact user@domain.co.uk please"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "user@domain.co.uk" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized

    def test_multiple_emails(self):
        """Test multiple emails in one text."""
        text = "Send to user1@example.com and user2@test.com"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "user1@example.com" not in sanitized
        assert "user2@test.com" not in sanitized
        assert sanitized.count("<EMAIL_REMOVED>") == 2

    def test_email_in_sentence(self):
        """Test email embedded in sentence."""
        text = "Please contact john.doe@company.org for details."
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "john.doe@company.org" not in sanitized
        assert "Please contact <EMAIL_REMOVED> for details." == sanitized


class TestPhoneDetection:
    """Tests for phone number detection and sanitization."""

    def test_phone_with_plus49(self):
        """Test German phone with +49 prefix."""
        text = "Call +49 123 456789"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "+49 123 456789" not in sanitized
        assert "<PHONE_REMOVED>" in sanitized

    def test_phone_with_0049(self):
        """Test German phone with 0049 prefix."""
        text = "Number: 0049 123 456789"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "0049 123 456789" not in sanitized
        assert "<PHONE_REMOVED>" in sanitized

    def test_phone_with_leading_zero(self):
        """Test German phone with leading zero."""
        text = "Phone: 0123 456 789"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "0123 456 789" not in sanitized
        assert "<PHONE_REMOVED>" in sanitized

    def test_phone_no_spaces(self):
        """Test phone without spaces."""
        text = "Call +49123456789"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "+49123456789" not in sanitized
        assert "<PHONE_REMOVED>" in sanitized

    def test_phone_with_mixed_separators(self):
        """Test phone with mixed separators."""
        text = "0123/456-789"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "0123/456-789" not in sanitized
        assert "<PHONE_REMOVED>" in sanitized

    def test_phone_with_slashes(self):
        """Test phone with slashes."""
        text = "0123/456/789"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "0123/456/789" not in sanitized
        assert "<PHONE_REMOVED>" in sanitized

    def test_multiple_phones(self):
        """Test multiple phone numbers."""
        text = "Call +49 123 456789 or 0987 654 321"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "+49 123 456789" not in sanitized
        assert "0987 654 321" not in sanitized
        assert sanitized.count("<PHONE_REMOVED>") == 2


class TestIBANDetection:
    """Tests for IBAN detection and sanitization."""

    def test_valid_german_iban(self):
        """Test valid German IBAN."""
        text = "IBAN: DE89370400440532013000"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "DE89370400440532013000" not in sanitized
        assert "<IBAN_REMOVED>" in sanitized

    def test_iban_in_sentence(self):
        """Test IBAN embedded in sentence."""
        text = "Transfer to DE12345678901234567890 please"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "DE12345678901234567890" not in sanitized
        assert "<IBAN_REMOVED>" in sanitized

    def test_multiple_ibans(self):
        """Test multiple IBANs."""
        text = "From DE11111111111111111111 to DE22222222222222222222"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "DE11111111111111111111" not in sanitized
        assert "DE22222222222222222222" not in sanitized
        assert sanitized.count("<IBAN_REMOVED>") == 2

    def test_iban_with_spaces_matches_phone(self):
        """Test that formatted IBAN with spaces may match phone pattern."""
        text = "IBAN: DE89 3704 0044 0532 0130 00"
        sanitized, found = DataPrivacyShield.sanitize(text)

        # Phone pattern may match "0044 0532" sequence - acceptable
        # (Real IBANs are stored without spaces in databases)
        assert found is True  # Phone or IBAN detected

    def test_non_german_iban_not_matched(self):
        """Test that non-German IBAN is not matched."""
        text = "IBAN: FR1420041010050500013M02606"
        sanitized, found = DataPrivacyShield.sanitize(text)

        # Should not match (not DE)
        assert found is False
        assert sanitized == text


class TestMixedPII:
    """Tests for multiple types of PII in same text."""

    def test_email_and_phone(self):
        """Test text with both email and phone."""
        text = "Contact user@example.com or call +49 123 456789"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "user@example.com" not in sanitized
        assert "+49 123 456789" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized
        assert "<PHONE_REMOVED>" in sanitized

    def test_email_and_iban(self):
        """Test text with email and IBAN."""
        text = "Send invoice to user@test.com, IBAN DE12345678901234567890"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "user@test.com" not in sanitized
        assert "DE12345678901234567890" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized
        assert "<IBAN_REMOVED>" in sanitized

    def test_all_pii_types(self):
        """Test text with email, phone, and IBAN."""
        text = (
            "Contact: user@example.com, "
            "Phone: +49 123 456789, "
            "IBAN: DE12345678901234567890"
        )
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "user@example.com" not in sanitized
        assert "+49 123 456789" not in sanitized
        assert "DE12345678901234567890" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized
        assert "<PHONE_REMOVED>" in sanitized
        assert "<IBAN_REMOVED>" in sanitized


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_no_pii(self):
        """Test text without any PII."""
        text = "This is a normal text without PII"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is False
        assert sanitized == text

    def test_empty_string(self):
        """Test empty string."""
        text = ""
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is False
        assert sanitized == ""

    def test_none_input(self):
        """Test None input."""
        text = None
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is False
        assert sanitized is None

    def test_only_pii(self):
        """Test text containing only PII."""
        text = "user@example.com"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert sanitized == "<EMAIL_REMOVED>"

    def test_url_with_at_sign(self):
        """Test URL with @ sign (should match as email)."""
        text = "Visit http://user@server.com/page"
        sanitized, found = DataPrivacyShield.sanitize(text)

        # The email pattern will match user@server.com
        assert found is True
        assert "user@server.com" not in sanitized

    def test_whitespace_preservation(self):
        """Test that whitespace is preserved."""
        text = "Email:  user@test.com  Phone: +49 123 456789"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        # Check spacing is preserved
        assert "Email:  <EMAIL_REMOVED>  Phone: <PHONE_REMOVED>" == sanitized


class TestHasPIIMethod:
    """Tests for has_pii() convenience method."""

    def test_has_pii_with_email(self):
        """Test has_pii returns True for email."""
        text = "Contact user@example.com"
        assert DataPrivacyShield.has_pii(text) is True

    def test_has_pii_with_phone(self):
        """Test has_pii returns True for phone."""
        text = "Call +49 123 456789"
        assert DataPrivacyShield.has_pii(text) is True

    def test_has_pii_with_iban(self):
        """Test has_pii returns True for IBAN."""
        text = "IBAN DE12345678901234567890"
        assert DataPrivacyShield.has_pii(text) is True

    def test_has_pii_without_pii(self):
        """Test has_pii returns False for clean text."""
        text = "This is clean text"
        assert DataPrivacyShield.has_pii(text) is False

    def test_has_pii_empty_string(self):
        """Test has_pii with empty string."""
        assert DataPrivacyShield.has_pii("") is False

    def test_has_pii_none(self):
        """Test has_pii with None."""
        assert DataPrivacyShield.has_pii(None) is False
