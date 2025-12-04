import logging
import pytest
from app.core.logging import PrivacyLogFilter


class TestPrivacyLogFilter:
    """Tests for PrivacyLogFilter."""

    @pytest.fixture
    def filter(self):
        """Create a PrivacyLogFilter instance."""
        return PrivacyLogFilter()

    @pytest.fixture
    def log_record(self):
        """Create a basic LogRecord for testing."""
        return logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )

    def test_filter_sanitizes_email(self, filter, log_record):
        """Test that emails in log messages are redacted."""
        log_record.msg = "User email is test@example.com"
        filter.filter(log_record)
        
        assert "<EMAIL_REMOVED>" in log_record.msg
        assert "test@example.com" not in log_record.msg

    def test_filter_sanitizes_phone(self, filter, log_record):
        """Test that phone numbers in log messages are redacted."""
        log_record.msg = "Call +49 123 456789 for support"
        filter.filter(log_record)
        
        assert "<PHONE_REMOVED>" in log_record.msg
        assert "+49 123 456789" not in log_record.msg

    def test_filter_sanitizes_args(self, filter, log_record):
        """Test that PII in log arguments is redacted."""
        log_record.msg = "Contact: %s"
        log_record.args = ("+49 123 456789",)
        filter.filter(log_record)
        
        assert log_record.args[0] == "<PHONE_REMOVED>"

    def test_filter_ignores_non_pii(self, filter, log_record):
        """Test that non-PII messages are unchanged."""
        original_msg = "System started successfully"
        log_record.msg = original_msg
        filter.filter(log_record)
        
        assert log_record.msg == original_msg

    def test_filter_handles_mixed_content(self, filter, log_record):
        """Test mixed PII and normal content."""
        log_record.msg = "Error processing request for user@domain.com: Timeout"
        filter.filter(log_record)
        
        assert "user@domain.com" not in log_record.msg
        assert "<EMAIL_REMOVED>" in log_record.msg
        assert "Timeout" in log_record.msg

    def test_filter_returns_true(self, filter, log_record):
        """Test that filter always returns True (doesn't block records)."""
        result = filter.filter(log_record)
        assert result is True

    def test_filter_with_multiple_args(self, filter, log_record):
        """Test filtering with multiple arguments."""
        log_record.msg = "User %s logged in from %s"
        log_record.args = ("user@example.com", "192.168.1.1")
        filter.filter(log_record)
        
        assert log_record.args[0] == "<EMAIL_REMOVED>"
        assert log_record.args[1] == "192.168.1.1"  # IP not PII

    def test_filter_with_non_string_args(self, filter, log_record):
        """Test that non-string arguments are preserved."""
        log_record.msg = "Processing %d items"
        log_record.args = (42,)
        filter.filter(log_record)
        
        assert log_record.args[0] == 42
