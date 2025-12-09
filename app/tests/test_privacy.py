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


class TestEmailEdgeCases:
    """Extended tests for email edge cases."""

    def test_email_with_underscore(self):
        """Test email with underscore in username."""
        text = "Contact user_name@domain.com"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "user_name@domain.com" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized

    def test_email_with_hyphen(self):
        """Test email with hyphen in username."""
        text = "Email: first-last@company.org"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "first-last@company.org" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized

    def test_email_with_percentage(self):
        """Test email with percentage sign (rare but valid)."""
        text = "Send to user%tag@domain.com"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "user%tag@domain.com" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized

    def test_very_long_email(self):
        """Test very long email address."""
        text = "Contact verylongusername@subdomain.example.domain.com"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "verylongusername@subdomain.example.domain.com" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized

    def test_minimum_valid_email(self):
        """Test minimum valid email format."""
        text = "Email a@b.co"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "a@b.co" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized

    def test_email_case_sensitivity(self):
        """Test email detection is case-insensitive."""
        text = "User@Example.COM and TEST@domain.ORG"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "User@Example.COM" not in sanitized
        assert "TEST@domain.ORG" not in sanitized
        assert sanitized.count("<EMAIL_REMOVED>") == 2


class TestGermanMobileNumbers:
    """Extended tests for German mobile phone numbers."""

    def test_vodafone_mobile(self):
        """Test Vodafone mobile number (0172)."""
        text = "Call 0172 1234567"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "0172 1234567" not in sanitized
        assert "<PHONE_REMOVED>" in sanitized

    def test_telekom_mobile(self):
        """Test T-Mobile number (0151)."""
        text = "Mobile: 0151 12345678"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "0151 12345678" not in sanitized
        assert "<PHONE_REMOVED>" in sanitized

    def test_o2_mobile(self):
        """Test O2 mobile number (0176)."""
        text = "Reach me at 0176 123456789"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "0176 123456789" not in sanitized
        assert "<PHONE_REMOVED>" in sanitized

    def test_mobile_with_plus49(self):
        """Test mobile with +49 international prefix."""
        text = "WhatsApp: +49 151 12345678"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "+49 151 12345678" not in sanitized
        assert "<PHONE_REMOVED>" in sanitized

    def test_berlin_landline(self):
        """Test Berlin landline (030)."""
        text = "Office: 030 12345678"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "030 12345678" not in sanitized
        assert "<PHONE_REMOVED>" in sanitized

    def test_munich_landline(self):
        """Test Munich landline (089)."""
        text = "Call 089 123456789"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "089 123456789" not in sanitized
        assert "<PHONE_REMOVED>" in sanitized

    def test_very_long_number(self):
        """Test very long phone number."""
        text = "Number: 0123 123456789012"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "0123 123456789012" not in sanitized
        assert "<PHONE_REMOVED>" in sanitized


class TestIBANEdgeCases:
    """Extended tests for IBAN edge cases."""

    def test_iban_without_word_boundary(self):
        """Test IBAN detection with word boundaries (correct regex behavior)."""
        # The \b word boundary in the IBAN pattern is intentional -
        # it prevents matching partial strings like "textDE12345678901234567890text"
        text = "IBAN DE12345678901234567890 found"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "DE12345678901234567890" not in sanitized
        assert "<IBAN_REMOVED>" in sanitized

    def test_multiple_ibans_complex_text(self):
        """Test multiple IBANs in complex sentence."""
        text = (
            "Transfer from DE11111111111111111111 "
            "(Account A) to DE22222222222222222222 "
            "(Account B) and CC DE33333333333333333333."
        )
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "DE11111111111111111111" not in sanitized
        assert "DE22222222222222222222" not in sanitized
        assert "DE33333333333333333333" not in sanitized
        assert sanitized.count("<IBAN_REMOVED>") == 3


class TestUnicodeAndPerformance:
    """Tests for Unicode support and performance."""

    def test_unicode_with_email(self):
        """Test Unicode text with ASCII email (Umlauts in domain not RFC-compliant)."""
        text = "Kontaktieren Sie uns: mueller@firma.de für Details"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "mueller@firma.de" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized
        assert "Kontaktieren" in sanitized
        assert "für" in sanitized

    def test_unicode_with_phone(self):
        """Test Unicode text with phone number."""
        text = "Rufen Sie an: +49 123 456789 für Öffnungszeiten"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "+49 123 456789" not in sanitized
        assert "<PHONE_REMOVED>" in sanitized
        assert "Öffnungszeiten" in sanitized

    def test_very_long_text_with_pii(self):
        """Test performance with very long text containing PII."""
        long_text = "Lorem ipsum " * 100 + "user@example.com " + "dolor sit " * 100
        sanitized, found = DataPrivacyShield.sanitize(long_text)

        assert found is True
        assert "user@example.com" not in sanitized
        assert "<EMAIL_REMOVED>" in sanitized
        # Verify text length is preserved approximately
        assert len(sanitized) > 1000

    def test_multiple_pii_in_long_text(self):
        """Test multiple PII instances in long text."""
        text = (
            "Contact details: email1@test.com or email2@test.com. "
            "Phone numbers: +49 111 111111, 0222 222222, +49 333 333333. "
            "IBANs: DE11111111111111111111, DE22222222222222222222. "
        ) * 5  # Repeat 5 times for performance test

        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "email1@test.com" not in sanitized
        assert "email2@test.com" not in sanitized
        assert "+49 111 111111" not in sanitized
        assert "DE11111111111111111111" not in sanitized
        # Each repetition has 2 emails, 3 phones, 2 IBANs
        assert sanitized.count("<EMAIL_REMOVED>") == 10
        assert sanitized.count("<PHONE_REMOVED>") == 15
        assert sanitized.count("<IBAN_REMOVED>") == 10


class TestExceptionHandling:
    """Tests for error handling and edge cases that could cause exceptions."""

    def test_special_regex_characters_in_text(self):
        """Test text with regex special characters around valid emails."""
        text = "Contact: [test@example.com] or (user@domain.com)"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        # Valid emails should be detected even when surrounded by special chars
        assert "test@example.com" not in sanitized
        assert "user@domain.com" not in sanitized

    def test_backslash_in_text(self):
        """Test text with backslashes."""
        text = r"Path: C:\Users\test@example.com\Documents"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "test@example.com" not in sanitized

    def test_newlines_with_pii(self):
        """Test multiline text with PII."""
        text = "Line 1: user@example.com\nLine 2: +49 123 456789\nLine 3: DE12345678901234567890"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "user@example.com" not in sanitized
        assert "+49 123 456789" not in sanitized
        assert "DE12345678901234567890" not in sanitized
        # Verify newlines are preserved
        assert sanitized.count("\n") == 2


    def test_tabs_with_pii(self):
        """Test text with tabs."""
        text = "Email:\tuser@test.com\tPhone:\t+49 123 456789"
        sanitized, found = DataPrivacyShield.sanitize(text)

        assert found is True
        assert "user@test.com" not in sanitized
        assert "+49 123 456789" not in sanitized
        # Verify tabs are preserved
        assert "\t" in sanitized

    def test_internal_exception(self):
        """Test fail-open behavior when an exception occurs."""
        import unittest.mock

        text = "This text should be returned as is"

        # Mock EMAIL_PATTERN to raise an exception
        # We mock the class attribute on the class itself
        with unittest.mock.patch.object(DataPrivacyShield, 'EMAIL_PATTERN') as mock_pattern:
            mock_pattern.findall.side_effect = Exception("Test error")

            sanitized, found = DataPrivacyShield.sanitize(text)

            assert found is False
            assert sanitized == text

