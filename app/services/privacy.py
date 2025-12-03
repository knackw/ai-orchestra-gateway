"""
Data Privacy Shield for PII detection and sanitization.

Automatically detects and removes personally identifiable information (PII)
from text before sending to AI providers, ensuring DSGVO compliance.
"""

import logging
import re
from typing import Tuple

logger = logging.getLogger(__name__)


class DataPrivacyShield:
    """
    Privacy shield for detecting and sanitizing PII in text.

    Detects and replaces:
    - Email addresses
    - Phone numbers (German formats)
    - IBAN (German)
    """

    # Email pattern - comprehensive and permissive
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )

    # Phone pattern - German formats
    # Matches: +49 123 456789, 0123 456 789, +49-123-456-789, etc.
    # Processed after IBAN to avoid matching IBAN digit sequences
    PHONE_PATTERN = re.compile(
        r'(\+49|0049|0)\s?\d{2,5}[\s\-/]?\d{3,}[\s\-/]?\d{3,}\b'
    )

    # IBAN pattern - German only (DE + 20 digits)
    IBAN_PATTERN = re.compile(r'\bDE\d{20}\b')

    # Placeholders
    EMAIL_PLACEHOLDER = "<EMAIL_REMOVED>"
    PHONE_PLACEHOLDER = "<PHONE_REMOVED>"
    IBAN_PLACEHOLDER = "<IBAN_REMOVED>"

    @classmethod
    def sanitize(cls, text: str) -> Tuple[str, bool]:
        """
        Sanitize text by removing PII and replacing with placeholders.

        Args:
            text: Input text to sanitize

        Returns:
            Tuple of (sanitized_text, pii_found)
            - sanitized_text: Text with PII replaced by placeholders
            - pii_found: True if any PII was detected and removed

        Example:
            >>> text = "Contact me at user@example.com"
            >>> sanitized, found = DataPrivacyShield.sanitize(text)
            >>> print(sanitized)
            "Contact me at <EMAIL_REMOVED>"
            >>> print(found)
            True
        """
        if not text:
            return text, False

        try:
            sanitized = text
            pii_found = False
            detections = []

            # Detect and replace emails
            email_matches = cls.EMAIL_PATTERN.findall(sanitized)
            if email_matches:
                sanitized = cls.EMAIL_PATTERN.sub(
                    cls.EMAIL_PLACEHOLDER, sanitized
                )
                pii_found = True
                detections.append(f"email ({len(email_matches)})")

            # Detect and replace IBANs FIRST (before phone to avoid conflicts)
            iban_matches = cls.IBAN_PATTERN.findall(sanitized)
            if iban_matches:
                sanitized = cls.IBAN_PATTERN.sub(
                    cls.IBAN_PLACEHOLDER, sanitized
                )
                pii_found = True
                detections.append(f"IBAN ({len(iban_matches)})")

            # Detect and replace phone numbers (after IBAN)
            phone_matches = cls.PHONE_PATTERN.findall(sanitized)
            if phone_matches:
                sanitized = cls.PHONE_PATTERN.sub(
                    cls.PHONE_PLACEHOLDER, sanitized
                )
                pii_found = True
                detections.append(f"phone ({len(phone_matches)})")

            # Log PII detections (without logging actual PII!)
            if pii_found:
                logger.warning(
                    f"PII detected and sanitized: {', '.join(detections)}"
                )

            return sanitized, pii_found

        except Exception as e:
            logger.error(f"Error during sanitization: {e}")
            # Fail open - return original text but log the error
            return text, False

    @classmethod
    def has_pii(cls, text: str) -> bool:
        """
        Check if text contains any PII without sanitizing.

        Args:
            text: Text to check

        Returns:
            True if PII is detected, False otherwise
        """
        if not text:
            return False

        return bool(
            cls.EMAIL_PATTERN.search(text)
            or cls.PHONE_PATTERN.search(text)
            or cls.IBAN_PATTERN.search(text)
        )
