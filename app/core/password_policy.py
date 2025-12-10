"""
SEC-012: Password Policy Validation

Backend implementation of password policy matching the frontend (Zod) validation.
Ensures consistent password requirements across frontend and backend.

Requirements:
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- Not in the list of common/compromised passwords
"""

import re
from typing import Optional
from pydantic import BaseModel, field_validator


# SEC-012: Common passwords to block (subset - extend as needed)
COMMON_PASSWORDS = {
    "password123",
    "password1234",
    "qwerty123456",
    "letmein12345",
    "welcome12345",
    "admin1234567",
    "123456789012",
    "iloveyou1234",
    "sunshine1234",
    "princess1234",
    "football1234",
    "monkey123456",
    "shadow123456",
    "master123456",
    "dragon123456",
    "michael12345",
    "jennifer1234",
    "trustno1234",
    "hunter123456",
    "freedom12345",
    "whatever1234",
    "qazwsx123456",
    "123qwe123456",
    "abc123456789",
    "passw0rd1234",
    "p@ssw0rd1234",
    "p@ssword1234",
    "letmein!1234",
    "welcome!1234",
    "qwerty!12345",
    "password!234",
    "password@123",
    "summer123456",
    "winter123456",
    "spring123456",
    "autumn123456",
    "baseball1234",
    "superman1234",
    "starwars1234",
    "access123456",
    "mustang12345",
    "corvette1234",
    "mercedes1234",
    "passphrase12",
    "changeme1234",
    "letmein!2345",
    "administrator",
    "administrator1",
    "password1!@#",
    "qwertyuiop12",
    "asdfghjkl123",
    "zxcvbnm12345",
}

# Regex patterns for password requirements
UPPERCASE_PATTERN = re.compile(r"[A-Z]")
LOWERCASE_PATTERN = re.compile(r"[a-z]")
NUMBER_PATTERN = re.compile(r"[0-9]")
SPECIAL_CHAR_PATTERN = re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?~`]")


class PasswordValidationResult(BaseModel):
    """Result of password validation."""

    is_valid: bool
    errors: list[str] = []
    strength: str = "weak"  # weak, medium, strong, very_strong


def validate_password(password: str) -> PasswordValidationResult:
    """
    Validate password against security policy.

    SEC-012: Password must meet all requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    - Not a common password

    Returns:
        PasswordValidationResult with validation status and any errors
    """
    errors = []
    strength_score = 0

    # Check minimum length
    if len(password) < 12:
        errors.append("Passwort muss mindestens 12 Zeichen lang sein")
    else:
        strength_score += 1
        if len(password) >= 16:
            strength_score += 1

    # Check for uppercase
    if not UPPERCASE_PATTERN.search(password):
        errors.append("Passwort muss mindestens einen Großbuchstaben enthalten")
    else:
        strength_score += 1

    # Check for lowercase
    if not LOWERCASE_PATTERN.search(password):
        errors.append("Passwort muss mindestens einen Kleinbuchstaben enthalten")
    else:
        strength_score += 1

    # Check for number
    if not NUMBER_PATTERN.search(password):
        errors.append("Passwort muss mindestens eine Zahl enthalten")
    else:
        strength_score += 1

    # Check for special character
    if not SPECIAL_CHAR_PATTERN.search(password):
        errors.append("Passwort muss mindestens ein Sonderzeichen enthalten (!@#$%^&*)")
    else:
        strength_score += 1

    # Check against common passwords
    if password.lower() in COMMON_PASSWORDS:
        errors.append("Dieses Passwort ist zu häufig und unsicher")

    # Calculate strength
    if strength_score >= 6:
        strength = "very_strong"
    elif strength_score >= 5:
        strength = "strong"
    elif strength_score >= 3:
        strength = "medium"
    else:
        strength = "weak"

    return PasswordValidationResult(
        is_valid=len(errors) == 0, errors=errors, strength=strength
    )


def get_password_requirements() -> dict:
    """
    Get password requirements for API documentation.

    Returns dict with human-readable requirements.
    """
    return {
        "min_length": 12,
        "requirements": [
            "Mindestens 12 Zeichen",
            "Mindestens ein Großbuchstabe (A-Z)",
            "Mindestens ein Kleinbuchstabe (a-z)",
            "Mindestens eine Zahl (0-9)",
            "Mindestens ein Sonderzeichen (!@#$%^&*)",
        ],
        "requirements_en": [
            "At least 12 characters",
            "At least one uppercase letter (A-Z)",
            "At least one lowercase letter (a-z)",
            "At least one number (0-9)",
            "At least one special character (!@#$%^&*)",
        ],
    }


class PasswordField(str):
    """
    Custom Pydantic field type for password validation.

    Usage in Pydantic models:
        class ChangePasswordRequest(BaseModel):
            new_password: PasswordField
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Passwort muss eine Zeichenkette sein")

        result = validate_password(value)
        if not result.is_valid:
            raise ValueError("; ".join(result.errors))

        return value


# Pydantic model with password validation
class PasswordChangeRequest(BaseModel):
    """Request model for password change with validation."""

    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        result = validate_password(v)
        if not result.is_valid:
            raise ValueError("; ".join(result.errors))
        return v


class PasswordResetRequest(BaseModel):
    """Request model for password reset with validation."""

    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        result = validate_password(v)
        if not result.is_valid:
            raise ValueError("; ".join(result.errors))
        return v


# Export all
__all__ = [
    "validate_password",
    "get_password_requirements",
    "PasswordValidationResult",
    "PasswordField",
    "PasswordChangeRequest",
    "PasswordResetRequest",
    "COMMON_PASSWORDS",
]
