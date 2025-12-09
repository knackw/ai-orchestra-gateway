import logging
from app.services.privacy import DataPrivacyShield
from app.core.middleware import get_request_id


class PrivacyLogFilter(logging.Filter):
    """
    Logging filter that sanitizes PII from log records using DataPrivacyShield.
    Ensures that no sensitive data (emails, phone numbers, etc.) is written to logs.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record by sanitizing PII from message and arguments.
        """
        # Sanitize the main log message
        if isinstance(record.msg, str):
            record.msg, _ = DataPrivacyShield.sanitize(record.msg)
        
        # Handle arguments
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


class RequestIdFilter(logging.Filter):
    """
    Logging filter that adds the current request ID to log records.
    Ensures request_id is always present to prevent KeyError in log formatting.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        # Always set request_id, fallback to "system" if not in request context
        if not hasattr(record, 'request_id') or not record.request_id:
            record.request_id = get_request_id() or "system"
        return True
