import logging
from typing import Any
from app.services.privacy import DataPrivacyShield


class PrivacyLogFilter(logging.Filter):
    """
    Logging filter that sanitizes PII from log records using DataPrivacyShield.
    Ensures that no sensitive data (emails, phone numbers, etc.) is written to logs.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record by sanitizing PII from message and arguments.
        
        Args:
            record: LogRecord to filter
            
        Returns:
            True (always - we modify but don't block records)
        """
        # Sanitize the main log message
        if isinstance(record.msg, str):
            record.msg, _ = DataPrivacyShield.sanitize(record.msg)
        
        # Handle arguments if they are strings
        # Note: This handles cases like logger.info("User %s logged in", user_email)
        if record.args:
            new_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    sanitized_arg, _ = DataPrivacyShield.sanitize(arg)
                    new_args.append(sanitized_arg)
                else:
                    new_args.append(arg)
            record.args = tuple(new_args)

        return True
