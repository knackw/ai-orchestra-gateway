"""
Unit tests for Invoice Generation Service.

Tests:
- Invoice creation
- Invoice retrieval
- Payment processing
- PDF generation
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date, datetime, timezone
from decimal import Decimal

from app.core.i18n import Language
from app.services.invoice import (
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    InvoiceService,
    InvoiceConfig,
    get_invoice_service,
)


class TestInvoiceStatus:
    """Tests for InvoiceStatus enum."""

    def test_status_values(self):
        """Status values should match expected strings."""
        assert InvoiceStatus.DRAFT.value == "draft"
        assert InvoiceStatus.PENDING.value == "pending"
        assert InvoiceStatus.PAID.value == "paid"
        assert InvoiceStatus.OVERDUE.value == "overdue"
        assert InvoiceStatus.CANCELLED.value == "cancelled"
        assert InvoiceStatus.REFUNDED.value == "refunded"


class TestInvoice:
    """Tests for Invoice dataclass."""

    @pytest.fixture
    def sample_invoice(self):
        """Create sample invoice."""
        return Invoice(
            id="inv-123",
            invoice_number="INV-2025-00001",
            tenant_id="tenant-456",
            status=InvoiceStatus.PENDING,
            currency="EUR",
            subtotal_cents=10000,
            tax_rate_percent=Decimal("19.00"),
            tax_cents=1900,
            total_cents=11900,
            credits_purchased=100,
            price_per_credit_cents=100,
            due_date=date(2025, 12, 31),
        )

    def test_subtotal_property(self, sample_invoice):
        """Subtotal should return Decimal."""
        assert sample_invoice.subtotal == Decimal("100.00")

    def test_tax_property(self, sample_invoice):
        """Tax should return Decimal."""
        assert sample_invoice.tax == Decimal("19.00")

    def test_total_property(self, sample_invoice):
        """Total should return Decimal."""
        assert sample_invoice.total == Decimal("119.00")

    def test_is_paid_true(self):
        """is_paid should be True when status is PAID."""
        invoice = Invoice(
            id="inv-123",
            invoice_number="INV-2025-00001",
            tenant_id="tenant-456",
            status=InvoiceStatus.PAID,
            currency="EUR",
            subtotal_cents=10000,
            tax_rate_percent=Decimal("19.00"),
            tax_cents=1900,
            total_cents=11900,
            credits_purchased=100,
            price_per_credit_cents=100,
        )
        assert invoice.is_paid is True

    def test_is_paid_false(self, sample_invoice):
        """is_paid should be False when status is not PAID."""
        assert sample_invoice.is_paid is False

    def test_is_overdue_true(self):
        """is_overdue should be True when past due date."""
        invoice = Invoice(
            id="inv-123",
            invoice_number="INV-2025-00001",
            tenant_id="tenant-456",
            status=InvoiceStatus.PENDING,
            currency="EUR",
            subtotal_cents=10000,
            tax_rate_percent=Decimal("19.00"),
            tax_cents=1900,
            total_cents=11900,
            credits_purchased=100,
            price_per_credit_cents=100,
            due_date=date(2020, 1, 1),  # Past date
        )
        assert invoice.is_overdue is True

    def test_is_overdue_false_future(self, sample_invoice):
        """is_overdue should be False when due date is in future."""
        assert sample_invoice.is_overdue is False

    def test_is_overdue_false_paid(self):
        """is_overdue should be False when already paid."""
        invoice = Invoice(
            id="inv-123",
            invoice_number="INV-2025-00001",
            tenant_id="tenant-456",
            status=InvoiceStatus.PAID,
            currency="EUR",
            subtotal_cents=10000,
            tax_rate_percent=Decimal("19.00"),
            tax_cents=1900,
            total_cents=11900,
            credits_purchased=100,
            price_per_credit_cents=100,
            due_date=date(2020, 1, 1),  # Past date but paid
        )
        assert invoice.is_overdue is False


class TestInvoiceItem:
    """Tests for InvoiceItem dataclass."""

    def test_create_item(self):
        """Should create InvoiceItem with all fields."""
        item = InvoiceItem(
            description="AI Gateway Credits",
            quantity=100,
            unit_price_cents=100,
            total_cents=10000,
            item_type="credits",
            metadata={"sku": "CREDIT-100"},
        )

        assert item.description == "AI Gateway Credits"
        assert item.quantity == 100
        assert item.unit_price_cents == 100
        assert item.total_cents == 10000
        assert item.item_type == "credits"
        assert item.metadata["sku"] == "CREDIT-100"


class TestInvoiceConfig:
    """Tests for InvoiceConfig."""

    def test_default_config(self):
        """Default config should have sensible defaults."""
        config = InvoiceConfig()
        assert config.default_currency == "EUR"
        assert config.default_tax_rate == Decimal("19.00")
        assert config.default_due_days == 30
        assert config.company_name == "AI Orchestra Gateway"

    def test_custom_config(self):
        """Should allow custom configuration."""
        config = InvoiceConfig(
            default_currency="USD",
            default_tax_rate=Decimal("10.00"),
            default_due_days=14,
            company_name="My Company",
            company_address="123 Main St",
            company_vat_id="DE123456789",
        )
        assert config.default_currency == "USD"
        assert config.default_tax_rate == Decimal("10.00")
        assert config.default_due_days == 14
        assert config.company_name == "My Company"


class TestInvoiceService:
    """Tests for InvoiceService."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Supabase client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def service(self, mock_client):
        """Create invoice service with mock client."""
        svc = InvoiceService()
        svc._client = mock_client
        return svc

    @pytest.mark.asyncio
    async def test_create_invoice(self, service, mock_client):
        """Should create invoice via RPC."""
        mock_client.rpc.return_value.execute.return_value.data = "inv-new-123"

        # Mock get_invoice for the return
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "id": "inv-new-123",
            "invoice_number": "INV-2025-00001",
            "tenant_id": "tenant-456",
            "status": "pending",
            "currency": "EUR",
            "subtotal_cents": 10000,
            "tax_rate_percent": "19.00",
            "tax_cents": 1900,
            "total_cents": 11900,
            "credits_purchased": 100,
            "price_per_credit_cents": 100,
        }

        # Mock items query
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []

        result = await service.create_invoice(
            tenant_id="tenant-456",
            credits=100,
            price_per_credit_cents=100,
            billing_name="Test Customer",
        )

        assert result is not None
        mock_client.rpc.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_invoice(self, service, mock_client):
        """Should get invoice by ID."""
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "id": "inv-123",
            "invoice_number": "INV-2025-00001",
            "tenant_id": "tenant-456",
            "status": "pending",
            "currency": "EUR",
            "subtotal_cents": 10000,
            "tax_rate_percent": "19.00",
            "tax_cents": 1900,
            "total_cents": 11900,
            "credits_purchased": 100,
            "price_per_credit_cents": 100,
        }

        # Mock items query
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [
            {
                "description": "AI Gateway Credits",
                "quantity": 100,
                "unit_price_cents": 100,
                "total_cents": 10000,
                "item_type": "credits",
                "metadata": {},
            }
        ]

        result = await service.get_invoice("inv-123")

        assert result is not None
        assert result.id == "inv-123"
        assert result.invoice_number == "INV-2025-00001"
        assert result.status == InvoiceStatus.PENDING
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_get_invoice_not_found(self, service, mock_client):
        """Should return None when invoice not found."""
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None

        result = await service.get_invoice("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_list_invoices(self, service, mock_client):
        """Should list invoices for tenant."""
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = [
            {
                "id": "inv-1",
                "invoice_number": "INV-2025-00001",
                "tenant_id": "tenant-456",
                "status": "paid",
                "currency": "EUR",
                "subtotal_cents": 10000,
                "tax_rate_percent": "19.00",
                "tax_cents": 1900,
                "total_cents": 11900,
                "credits_purchased": 100,
                "price_per_credit_cents": 100,
            },
            {
                "id": "inv-2",
                "invoice_number": "INV-2025-00002",
                "tenant_id": "tenant-456",
                "status": "pending",
                "currency": "EUR",
                "subtotal_cents": 5000,
                "tax_rate_percent": "19.00",
                "tax_cents": 950,
                "total_cents": 5950,
                "credits_purchased": 50,
                "price_per_credit_cents": 100,
            },
        ]

        result = await service.list_invoices("tenant-456")

        assert len(result) == 2
        assert result[0].invoice_number == "INV-2025-00001"
        assert result[1].invoice_number == "INV-2025-00002"

    @pytest.mark.asyncio
    async def test_list_invoices_with_status_filter(self, service, mock_client):
        """Should filter invoices by status."""
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.eq.return_value.execute.return_value.data = []

        await service.list_invoices("tenant-456", status=InvoiceStatus.PENDING)

        # Verify eq was called for status
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.eq.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_paid(self, service, mock_client):
        """Should mark invoice as paid via RPC."""
        mock_client.rpc.return_value.execute.return_value.data = True

        result = await service.mark_paid(
            invoice_id="inv-123",
            payment_method="stripe",
            payment_reference="pi_123456",
        )

        assert result is True
        mock_client.rpc.assert_called_once_with(
            "mark_invoice_paid",
            {
                "p_invoice_id": "inv-123",
                "p_payment_method": "stripe",
                "p_payment_reference": "pi_123456",
            },
        )

    @pytest.mark.asyncio
    async def test_mark_paid_failure(self, service, mock_client):
        """Should return False on payment failure."""
        mock_client.rpc.return_value.execute.return_value.data = False

        result = await service.mark_paid("inv-123")

        assert result is False

    @pytest.mark.asyncio
    async def test_cancel_invoice(self, service, mock_client):
        """Should cancel pending invoice."""
        mock_client.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"id": "inv-123"}
        ]

        result = await service.cancel_invoice("inv-123")

        assert result is True

    @pytest.mark.asyncio
    async def test_cancel_invoice_not_pending(self, service, mock_client):
        """Should fail to cancel non-pending invoice."""
        mock_client.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        result = await service.cancel_invoice("inv-123")

        assert result is False


class TestPDFGeneration:
    """Tests for PDF generation."""

    @pytest.fixture
    def service(self):
        """Create invoice service."""
        return InvoiceService(InvoiceConfig(
            company_name="Test Company",
            company_address="Test Address",
            company_vat_id="DE123456789",
        ))

    @pytest.fixture
    def sample_invoice(self):
        """Create sample invoice for PDF."""
        return Invoice(
            id="inv-123",
            invoice_number="INV-2025-00001",
            tenant_id="tenant-456",
            status=InvoiceStatus.PENDING,
            currency="EUR",
            subtotal_cents=10000,
            tax_rate_percent=Decimal("19.00"),
            tax_cents=1900,
            total_cents=11900,
            credits_purchased=100,
            price_per_credit_cents=100,
            billing_name="Test Customer",
            billing_email="customer@test.com",
            billing_address="Customer Address",
            due_date=date(2025, 12, 31),
            created_at=datetime(2025, 12, 1, 12, 0, 0, tzinfo=timezone.utc),
            items=[
                InvoiceItem(
                    description="AI Gateway Credits",
                    quantity=100,
                    unit_price_cents=100,
                    total_cents=10000,
                    item_type="credits",
                )
            ],
        )

    def test_generate_pdf(self, service, sample_invoice):
        """Should generate PDF bytes."""
        pdf = service.generate_pdf(sample_invoice)

        assert isinstance(pdf, bytes)
        assert len(pdf) > 0

    def test_pdf_contains_invoice_number(self, service, sample_invoice):
        """PDF should contain invoice number."""
        pdf = service.generate_pdf(sample_invoice)
        content = pdf.decode("utf-8")

        assert "INV-2025-00001" in content

    def test_pdf_contains_company_info(self, service, sample_invoice):
        """PDF should contain company info."""
        pdf = service.generate_pdf(sample_invoice)
        content = pdf.decode("utf-8")

        assert "Test Company" in content
        assert "Test Address" in content
        assert "DE123456789" in content

    def test_pdf_contains_billing_info(self, service, sample_invoice):
        """PDF should contain billing info."""
        pdf = service.generate_pdf(sample_invoice)
        content = pdf.decode("utf-8")

        assert "Test Customer" in content
        assert "customer@test.com" in content

    def test_pdf_contains_items(self, service, sample_invoice):
        """PDF should contain line items."""
        pdf = service.generate_pdf(sample_invoice)
        content = pdf.decode("utf-8")

        assert "AI Gateway Credits" in content

    def test_pdf_contains_totals(self, service, sample_invoice):
        """PDF should contain totals."""
        pdf = service.generate_pdf(sample_invoice)
        content = pdf.decode("utf-8")

        assert "Subtotal" in content
        assert "Tax" in content
        assert "TOTAL" in content

    def test_pdf_paid_invoice(self, service):
        """PDF should show payment info for paid invoice."""
        invoice = Invoice(
            id="inv-123",
            invoice_number="INV-2025-00001",
            tenant_id="tenant-456",
            status=InvoiceStatus.PAID,
            currency="EUR",
            subtotal_cents=10000,
            tax_rate_percent=Decimal("19.00"),
            tax_cents=1900,
            total_cents=11900,
            credits_purchased=100,
            price_per_credit_cents=100,
            payment_method="stripe",
            payment_reference="pi_123456",
            paid_at=datetime(2025, 12, 5, 12, 0, 0, tzinfo=timezone.utc),
            items=[],
        )

        pdf = service.generate_pdf(invoice)
        content = pdf.decode("utf-8")

        assert "PAID" in content
        assert "stripe" in content
        assert "pi_123456" in content


class TestAmountFormatting:
    """Tests for amount formatting."""

    @pytest.fixture
    def service(self):
        """Create invoice service."""
        return InvoiceService()

    def test_format_eur(self, service):
        """Should format EUR amounts correctly."""
        result = service.format_amount(10000, "EUR")
        assert result == "€100.00"

    def test_format_usd(self, service):
        """Should format USD amounts correctly."""
        result = service.format_amount(10000, "USD")
        assert result == "$100.00"

    def test_format_other_currency(self, service):
        """Should format other currencies with code."""
        result = service.format_amount(10000, "GBP")
        assert result == "GBP 100.00"

    def test_format_with_thousands(self, service):
        """Should format large amounts with thousands separator."""
        result = service.format_amount(100000000, "EUR")
        assert result == "€1,000,000.00"

    def test_format_cents(self, service):
        """Should handle cent amounts correctly."""
        result = service.format_amount(99, "EUR")
        assert result == "€0.99"


class TestGetInvoiceService:
    """Tests for global invoice service singleton."""

    def test_returns_instance(self):
        """Should return InvoiceService instance."""
        service = get_invoice_service()
        assert isinstance(service, InvoiceService)

    def test_singleton(self):
        """Should return same instance on multiple calls."""
        service1 = get_invoice_service()
        service2 = get_invoice_service()
        assert service1 is service2


class TestDateParsing:
    """Tests for date parsing utilities."""

    @pytest.fixture
    def service(self):
        """Create invoice service."""
        return InvoiceService()

    def test_parse_date_iso(self, service):
        """Should parse ISO date string."""
        result = service._parse_date("2025-12-01")
        assert result == date(2025, 12, 1)

    def test_parse_date_with_time(self, service):
        """Should parse datetime string to date."""
        result = service._parse_date("2025-12-01T12:00:00+00:00")
        assert result == date(2025, 12, 1)

    def test_parse_date_none(self, service):
        """Should return None for None input."""
        result = service._parse_date(None)
        assert result is None

    def test_parse_date_invalid(self, service):
        """Should return None for invalid input."""
        result = service._parse_date("invalid")
        assert result is None

    def test_parse_datetime_iso(self, service):
        """Should parse ISO datetime string."""
        result = service._parse_datetime("2025-12-01T12:00:00+00:00")
        assert result == datetime(2025, 12, 1, 12, 0, 0, tzinfo=timezone.utc)

    def test_parse_datetime_with_z(self, service):
        """Should parse datetime with Z suffix."""
        result = service._parse_datetime("2025-12-01T12:00:00Z")
        assert result is not None
        assert result.year == 2025

    def test_parse_datetime_none(self, service):
        """Should return None for None input."""
        result = service._parse_datetime(None)
        assert result is None
