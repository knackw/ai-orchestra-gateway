#!/usr/bin/env python3
"""
SEC-013: License Key Migration Script

Migrates plaintext license keys to SHA-256 hashed storage.

IMPORTANT: This is a ONE-WAY migration. Once keys are hashed, the original
plaintext keys cannot be recovered from the database. Ensure:

1. You have notified all customers about the key migration
2. You have a backup of the current database
3. You have tested the migration in a staging environment
4. You have a plan for customers who lose their keys

Usage:
    # Dry run (no changes)
    python scripts/migrate_license_keys.py --dry-run

    # Migrate all plaintext keys
    python scripts/migrate_license_keys.py --migrate

    # Migrate specific license
    python scripts/migrate_license_keys.py --migrate --license-id <uuid>

Environment:
    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables.
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timezone
from typing import Optional

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client, Client

from app.core.license_hash import (
    hash_license_key,
    is_hashed_key,
    mask_license_key,
    HASH_PREFIX,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LicenseKeyMigration:
    """Handles migration of plaintext license keys to hashed storage."""

    def __init__(self, dry_run: bool = True):
        """
        Initialize the migration.

        Args:
            dry_run: If True, don't make any changes to the database
        """
        self.dry_run = dry_run
        self.client = self._get_supabase_client()
        self.stats = {
            'total': 0,
            'already_hashed': 0,
            'migrated': 0,
            'errors': 0,
        }

    def _get_supabase_client(self) -> Client:
        """Get Supabase client with service role key."""
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

        if not url or not key:
            raise EnvironmentError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set"
            )

        return create_client(url, key)

    def get_licenses(self, license_id: Optional[str] = None) -> list:
        """
        Get licenses to migrate.

        Args:
            license_id: Optional specific license ID to migrate

        Returns:
            List of license records
        """
        query = self.client.table("licenses").select("id, license_key, tenant_id, name")

        if license_id:
            query = query.eq("id", license_id)

        response = query.execute()
        return response.data or []

    def should_migrate(self, license_key: str) -> bool:
        """
        Check if a license key needs migration.

        Args:
            license_key: The stored license key

        Returns:
            True if the key is plaintext and needs hashing
        """
        # Already hashed
        if is_hashed_key(license_key):
            return False

        # Empty or invalid
        if not license_key or not license_key.strip():
            return False

        return True

    def migrate_license(self, license_record: dict) -> bool:
        """
        Migrate a single license key to hashed storage.

        Args:
            license_record: The license record from the database

        Returns:
            True if migration was successful
        """
        license_id = license_record['id']
        license_key = license_record['license_key']
        tenant_id = license_record['tenant_id']
        name = license_record.get('name', 'Unknown')

        if not self.should_migrate(license_key):
            logger.info(
                f"Skipping {mask_license_key(license_key)} - already hashed"
            )
            self.stats['already_hashed'] += 1
            return True

        # Generate the hash
        hashed_key = hash_license_key(license_key)

        logger.info(
            f"{'[DRY RUN] ' if self.dry_run else ''}"
            f"Migrating license '{name}' for tenant {tenant_id}: "
            f"{mask_license_key(license_key)} -> {hashed_key[:20]}..."
        )

        if self.dry_run:
            self.stats['migrated'] += 1
            return True

        try:
            # Update the database
            response = (
                self.client.table("licenses")
                .update({
                    "license_key": hashed_key,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                })
                .eq("id", license_id)
                .execute()
            )

            if response.data:
                logger.info(f"Successfully migrated license {license_id}")
                self.stats['migrated'] += 1

                # Log to audit table if it exists
                self._log_audit(license_id, tenant_id)

                return True
            else:
                logger.error(f"Failed to update license {license_id}: No data returned")
                self.stats['errors'] += 1
                return False

        except Exception as e:
            logger.error(f"Error migrating license {license_id}: {e}")
            self.stats['errors'] += 1
            return False

    def _log_audit(self, license_id: str, tenant_id: str):
        """Log the migration to the audit table."""
        try:
            self.client.table("audit_logs").insert({
                "tenant_id": tenant_id,
                "action": "license.key_hashed",
                "resource_type": "license",
                "resource_id": license_id,
                "details": {
                    "migration": "SEC-013",
                    "description": "License key migrated to hashed storage",
                },
                "created_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
        except Exception as e:
            # Don't fail the migration if audit log fails
            logger.warning(f"Could not create audit log: {e}")

    def run(self, license_id: Optional[str] = None):
        """
        Run the migration.

        Args:
            license_id: Optional specific license ID to migrate
        """
        mode = "DRY RUN" if self.dry_run else "LIVE MIGRATION"
        logger.info(f"=" * 60)
        logger.info(f"SEC-013: License Key Migration - {mode}")
        logger.info(f"=" * 60)

        # Get licenses
        licenses = self.get_licenses(license_id)
        self.stats['total'] = len(licenses)

        logger.info(f"Found {len(licenses)} license(s) to process")

        if not licenses:
            logger.info("No licenses found to migrate")
            return

        # Process each license
        for license_record in licenses:
            self.migrate_license(license_record)

        # Print summary
        logger.info("")
        logger.info(f"=" * 60)
        logger.info("Migration Summary")
        logger.info(f"=" * 60)
        logger.info(f"Total licenses:    {self.stats['total']}")
        logger.info(f"Already hashed:    {self.stats['already_hashed']}")
        logger.info(f"Migrated:          {self.stats['migrated']}")
        logger.info(f"Errors:            {self.stats['errors']}")

        if self.dry_run:
            logger.info("")
            logger.info("This was a DRY RUN. No changes were made.")
            logger.info("Run with --migrate to perform the actual migration.")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate plaintext license keys to hashed storage"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Run in dry-run mode (default: True)'
    )
    parser.add_argument(
        '--migrate',
        action='store_true',
        help='Actually perform the migration'
    )
    parser.add_argument(
        '--license-id',
        type=str,
        help='Migrate only a specific license by ID'
    )

    args = parser.parse_args()

    # --migrate overrides --dry-run
    dry_run = not args.migrate

    if not dry_run:
        confirm = input(
            "\n*** WARNING ***\n"
            "This will permanently hash all plaintext license keys.\n"
            "This operation cannot be undone!\n\n"
            "Have you:\n"
            "  1. Backed up the database? (yes/no): "
        )
        if confirm.lower() != 'yes':
            print("Migration cancelled.")
            sys.exit(0)

        confirm = input("  2. Notified customers about key changes? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Please notify customers before migration.")
            sys.exit(0)

        confirm = input("  3. Tested in staging environment? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Please test in staging first.")
            sys.exit(0)

        final_confirm = input("\nType 'MIGRATE' to proceed: ")
        if final_confirm != 'MIGRATE':
            print("Migration cancelled.")
            sys.exit(0)

    try:
        migration = LicenseKeyMigration(dry_run=dry_run)
        migration.run(license_id=args.license_id)
    except EnvironmentError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
