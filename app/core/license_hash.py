"""
SEC-013: License Key Hashing Utilities

Provides secure hashing for license keys stored in the database.
Uses SHA-256 with a prefix for integrity verification.

IMPORTANT: This is a one-way migration. Once license keys are hashed,
the original keys cannot be recovered. Ensure you have a plan for
key rotation before implementing.
"""

import hashlib
import secrets
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Prefix for hashed license keys to identify them
HASH_PREFIX = "sha256:"

# Length of generated license keys (before hashing)
LICENSE_KEY_LENGTH = 32


def generate_license_key() -> str:
    """
    Generate a new cryptographically secure license key.

    Returns:
        A secure random string suitable for use as a license key.
        Format: lic_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX (36 chars total)
    """
    random_part = secrets.token_urlsafe(LICENSE_KEY_LENGTH)[:LICENSE_KEY_LENGTH]
    return f"lic_{random_part}"


def hash_license_key(license_key: str) -> str:
    """
    Hash a license key using SHA-256.

    The hash is prefixed with 'sha256:' to identify hashed keys.

    Args:
        license_key: The plaintext license key to hash

    Returns:
        The hashed license key with prefix (e.g., 'sha256:abc123...')
    """
    # Normalize the key
    key_bytes = license_key.strip().encode('utf-8')

    # Create SHA-256 hash
    hash_obj = hashlib.sha256(key_bytes)
    hash_hex = hash_obj.hexdigest()

    return f"{HASH_PREFIX}{hash_hex}"


def is_hashed_key(stored_key: str) -> bool:
    """
    Check if a stored key is already hashed.

    Args:
        stored_key: The key from the database

    Returns:
        True if the key is hashed, False if plaintext
    """
    return stored_key.startswith(HASH_PREFIX)


def verify_license_key(
    provided_key: str,
    stored_key: str
) -> bool:
    """
    Verify a provided license key against a stored key.

    Supports both hashed and plaintext stored keys for backwards compatibility
    during migration.

    Args:
        provided_key: The license key provided by the client
        stored_key: The key stored in the database (hashed or plaintext)

    Returns:
        True if the keys match, False otherwise
    """
    if is_hashed_key(stored_key):
        # Compare hashes
        provided_hash = hash_license_key(provided_key)
        return secrets.compare_digest(provided_hash, stored_key)
    else:
        # Legacy: plaintext comparison with constant-time comparison
        return secrets.compare_digest(provided_key, stored_key)


def get_key_for_lookup(license_key: str) -> Tuple[str, str]:
    """
    Get both the original key and its hash for database lookup.

    During migration, we need to check both plaintext and hashed keys.

    Args:
        license_key: The plaintext license key

    Returns:
        Tuple of (plaintext_key, hashed_key) for database queries
    """
    return (license_key, hash_license_key(license_key))


def migrate_key_to_hash(plaintext_key: str) -> dict:
    """
    Prepare a license key for migration to hashed storage.

    Returns the data needed to update the database.

    Args:
        plaintext_key: The current plaintext license key

    Returns:
        Dict with 'license_key_hash' to store in the database
    """
    return {
        'license_key_hash': hash_license_key(plaintext_key)
    }


# Utility for admin endpoints
def mask_license_key(license_key: str, visible_chars: int = 8) -> str:
    """
    Mask a license key for safe display.

    Args:
        license_key: The license key to mask
        visible_chars: Number of characters to show at the start

    Returns:
        Masked key like 'lic_abc1...xxxx'
    """
    if len(license_key) <= visible_chars:
        return '*' * len(license_key)

    prefix = license_key[:visible_chars]
    suffix_length = min(4, len(license_key) - visible_chars)
    suffix = license_key[-suffix_length:] if suffix_length > 0 else ''

    return f"{prefix}...{suffix}"
