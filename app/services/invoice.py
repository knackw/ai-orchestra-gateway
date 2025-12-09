"""
Invoice Generation Service for AI Gateway.

Provides invoice creation, management, and PDF generation for billing.
"""

import io
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import BinaryIO

from app.core.database import get_supabase_client
from app.core.i18n import Language, t

logger = logging.getLogger(__name__)


class InvoiceStatus(str, Enum):
    """Invoice status values."""
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass
class InvoiceItem:
    """Invoice line item."""
    description: str
    quantity: int
    unit_price_cents: int
    total_cents: int
    item_type: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class Invoice:
    """Invoice data model."""
    id: str
    invoice_number: str
    tenant_id: str
    status: InvoiceStatus
    currency: str

    # Amounts
    subtotal_cents: int
    tax_rate_percent: Decimal
    tax_cents: int
    total_cents: int

    # Credits
    credits_purchased: int
    price_per_credit_cents: int

    # Billing details
    billing_name: str | None = None
    billing_email: str | None = None
    billing_address: str | None = None
    billing_vat_id: str | None = None

    # Payment info
    payment_method: str | None = None
    payment_reference: str | None = None
    paid_at: datetime | None = None

    # Period
    period_start: date | None = None
    period_end: date | None = None
    due_date: date | None = None

    # Metadata
    notes: str | None = None
    metadata: dict = field(default_factory=dict)

    # Items
    items: list[InvoiceItem] = field(default_factory=list)

    # Timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def subtotal(self) -> Decimal:
        """Subtotal as Decimal."""
        return Decimal(self.subtotal_cents) / 100

    @property
    def tax(self) -> Decimal:
        """Tax amount as Decimal."""
        return Decimal(self.tax_cents) / 100

    @property
    def total(self) -> Decimal:
        """Total amount as Decimal."""
        return Decimal(self.total_cents) / 100

    @property
    def is_paid(self) -> bool:
        """Check if invoice is paid."""
        return self.status == InvoiceStatus.PAID

    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue."""
        if self.status != InvoiceStatus.PENDING:
            return False
        if self.due_date is None:
            return False
        return date.today() > self.due_date


@dataclass
class InvoiceConfig:
    """Invoice service configuration."""
    default_currency: str = "EUR"
    default_tax_rate: Decimal = Decimal("19.00")
    default_due_days: int = 30
    company_name: str = "AI Orchestra Gateway"
    company_address: str = ""
    company_vat_id: str = ""


class InvoiceService:
    """
    Invoice service for creating and managing invoices.

    Features:
    - Create invoices for credit purchases
    - Generate PDF invoices
    - Track payment status
    - Calculate tax
    """

    def __init__(self, config: InvoiceConfig | None = None):
        """
        Initialize invoice service.

        Args:
            config: Invoice configuration
        """
        self.config = config or InvoiceConfig()
        self._client = None

    def _get_client(self):
        """Get Supabase client (lazy loading)."""
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    def _parse_date(self, value: str | None) -> date | None:
        """Parse date string."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except (ValueError, AttributeError):
            return None

    def _parse_datetime(self, value: str | None) -> datetime | None:
        """Parse datetime string."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    async def create_invoice(
        self,
        tenant_id: str,
        credits: int,
        price_per_credit_cents: int = 1,
        billing_name: str | None = None,
        billing_email: str | None = None,
        billing_address: str | None = None,
        billing_vat_id: str | None = None,
        tax_rate_percent: Decimal | None = None,
        due_days: int | None = None,
        notes: str | None = None,
    ) -> Invoice | None:
        """
        Create a new invoice for credit purchase.

        Args:
            tenant_id: Tenant UUID
            credits: Number of credits to purchase
            price_per_credit_cents: Price per credit in cents
            billing_name: Customer billing name
            billing_email: Customer billing email
            billing_address: Customer billing address
            billing_vat_id: Customer VAT ID
            tax_rate_percent: Tax rate (defaults to config)
            due_days: Days until due (defaults to config)
            notes: Additional notes

        Returns:
            Created Invoice or None on error
        """
        try:
            client = self._get_client()

            tax_rate = tax_rate_percent or self.config.default_tax_rate
            days = due_days or self.config.default_due_days

            # Call database function
            response = client.rpc(
                "create_invoice",
                {
                    "p_tenant_id": tenant_id,
                    "p_credits": credits,
                    "p_price_per_credit_cents": price_per_credit_cents,
                    "p_tax_rate_percent": float(tax_rate),
                    "p_billing_name": billing_name,
                    "p_billing_email": billing_email,
                    "p_billing_address": billing_address,
                    "p_billing_vat_id": billing_vat_id,
                    "p_due_days": days,
                },
            ).execute()

            if not response.data:
                logger.error("Failed to create invoice - no ID returned")
                return None

            invoice_id = response.data

            # Update notes if provided
            if notes:
                client.table("invoices").update(
                    {"notes": notes}
                ).eq("id", invoice_id).execute()

            # Fetch and return the full invoice
            return await self.get_invoice(invoice_id)

        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            return None

    async def get_invoice(self, invoice_id: str) -> Invoice | None:
        """
        Get invoice by ID.

        Args:
            invoice_id: Invoice UUID

        Returns:
            Invoice or None if not found
        """
        try:
            client = self._get_client()

            # Get invoice
            response = (
                client.table("invoices")
                .select("*")
                .eq("id", invoice_id)
                .single()
                .execute()
            )

            if not response.data:
                return None

            data = response.data

            # Get items
            items_response = (
                client.table("invoice_items")
                .select("*")
                .eq("invoice_id", invoice_id)
                .order("sort_order")
                .execute()
            )

            items = [
                InvoiceItem(
                    description=item["description"],
                    quantity=item["quantity"],
                    unit_price_cents=item["unit_price_cents"],
                    total_cents=item["total_cents"],
                    item_type=item.get("item_type"),
                    metadata=item.get("metadata", {}),
                )
                for item in (items_response.data or [])
            ]

            return Invoice(
                id=data["id"],
                invoice_number=data["invoice_number"],
                tenant_id=data["tenant_id"],
                status=InvoiceStatus(data["status"]),
                currency=data["currency"],
                subtotal_cents=data["subtotal_cents"],
                tax_rate_percent=Decimal(str(data["tax_rate_percent"])),
                tax_cents=data["tax_cents"],
                total_cents=data["total_cents"],
                credits_purchased=data["credits_purchased"],
                price_per_credit_cents=data["price_per_credit_cents"],
                billing_name=data.get("billing_name"),
                billing_email=data.get("billing_email"),
                billing_address=data.get("billing_address"),
                billing_vat_id=data.get("billing_vat_id"),
                payment_method=data.get("payment_method"),
                payment_reference=data.get("payment_reference"),
                paid_at=self._parse_datetime(data.get("paid_at")),
                period_start=self._parse_date(data.get("period_start")),
                period_end=self._parse_date(data.get("period_end")),
                due_date=self._parse_date(data.get("due_date")),
                notes=data.get("notes"),
                metadata=data.get("metadata", {}),
                items=items,
                created_at=self._parse_datetime(data.get("created_at")),
                updated_at=self._parse_datetime(data.get("updated_at")),
            )

        except Exception as e:
            logger.error(f"Error getting invoice: {e}")
            return None

    async def get_invoice_by_number(
        self,
        invoice_number: str,
    ) -> Invoice | None:
        """
        Get invoice by invoice number.

        Args:
            invoice_number: Invoice number (e.g., INV-2025-00001)

        Returns:
            Invoice or None if not found
        """
        try:
            client = self._get_client()

            response = (
                client.table("invoices")
                .select("id")
                .eq("invoice_number", invoice_number)
                .single()
                .execute()
            )

            if not response.data:
                return None

            return await self.get_invoice(response.data["id"])

        except Exception as e:
            logger.error(f"Error getting invoice by number: {e}")
            return None

    async def list_invoices(
        self,
        tenant_id: str,
        status: InvoiceStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Invoice]:
        """
        List invoices for a tenant.

        Args:
            tenant_id: Tenant UUID
            status: Optional status filter
            limit: Maximum results
            offset: Offset for pagination

        Returns:
            List of invoices
        """
        try:
            client = self._get_client()

            query = (
                client.table("invoices")
                .select("*")
                .eq("tenant_id", tenant_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
            )

            if status:
                query = query.eq("status", status.value)

            response = query.execute()

            invoices = []
            for data in response.data or []:
                invoice = Invoice(
                    id=data["id"],
                    invoice_number=data["invoice_number"],
                    tenant_id=data["tenant_id"],
                    status=InvoiceStatus(data["status"]),
                    currency=data["currency"],
                    subtotal_cents=data["subtotal_cents"],
                    tax_rate_percent=Decimal(str(data["tax_rate_percent"])),
                    tax_cents=data["tax_cents"],
                    total_cents=data["total_cents"],
                    credits_purchased=data["credits_purchased"],
                    price_per_credit_cents=data["price_per_credit_cents"],
                    billing_name=data.get("billing_name"),
                    billing_email=data.get("billing_email"),
                    paid_at=self._parse_datetime(data.get("paid_at")),
                    due_date=self._parse_date(data.get("due_date")),
                    created_at=self._parse_datetime(data.get("created_at")),
                )
                invoices.append(invoice)

            return invoices

        except Exception as e:
            logger.error(f"Error listing invoices: {e}")
            return []

    async def mark_paid(
        self,
        invoice_id: str,
        payment_method: str = "stripe",
        payment_reference: str | None = None,
    ) -> bool:
        """
        Mark invoice as paid and add credits.

        Args:
            invoice_id: Invoice UUID
            payment_method: Payment method used
            payment_reference: Payment reference (transaction ID)

        Returns:
            True if successful
        """
        try:
            client = self._get_client()

            response = client.rpc(
                "mark_invoice_paid",
                {
                    "p_invoice_id": invoice_id,
                    "p_payment_method": payment_method,
                    "p_payment_reference": payment_reference,
                },
            ).execute()

            if response.data:
                logger.info(f"Invoice {invoice_id} marked as paid")
                return True
            return False

        except Exception as e:
            logger.error(f"Error marking invoice as paid: {e}")
            return False

    async def cancel_invoice(self, invoice_id: str) -> bool:
        """
        Cancel a pending invoice.

        Args:
            invoice_id: Invoice UUID

        Returns:
            True if successful
        """
        try:
            client = self._get_client()

            response = (
                client.table("invoices")
                .update({"status": "cancelled"})
                .eq("id", invoice_id)
                .eq("status", "pending")
                .execute()
            )

            if response.data:
                logger.info(f"Invoice {invoice_id} cancelled")
                return True
            return False

        except Exception as e:
            logger.error(f"Error cancelling invoice: {e}")
            return False

    def generate_pdf(
        self,
        invoice: Invoice,
        language: Language = Language.EN,
    ) -> bytes:
        """
        Generate PDF for invoice.

        Args:
            invoice: Invoice to generate PDF for
            language: Language for PDF content

        Returns:
            PDF bytes

        Note: This is a simplified text-based implementation.
        For production, use a proper PDF library like reportlab or weasyprint.
        """
        # Build invoice text content
        lines = []
        lines.append("=" * 60)
        lines.append(self.config.company_name)
        if self.config.company_address:
            lines.append(self.config.company_address)
        if self.config.company_vat_id:
            lines.append(f"VAT ID: {self.config.company_vat_id}")
        lines.append("=" * 60)
        lines.append("")

        # Invoice header
        lines.append(f"INVOICE: {invoice.invoice_number}")
        lines.append(f"Date: {invoice.created_at.strftime('%Y-%m-%d') if invoice.created_at else 'N/A'}")
        lines.append(f"Due Date: {invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else 'N/A'}")
        lines.append(f"Status: {invoice.status.value.upper()}")
        lines.append("")

        # Bill to
        lines.append("-" * 40)
        lines.append("BILL TO:")
        if invoice.billing_name:
            lines.append(invoice.billing_name)
        if invoice.billing_email:
            lines.append(invoice.billing_email)
        if invoice.billing_address:
            lines.append(invoice.billing_address)
        if invoice.billing_vat_id:
            lines.append(f"VAT ID: {invoice.billing_vat_id}")
        lines.append("")

        # Items
        lines.append("-" * 40)
        lines.append(f"{'Description':<30} {'Qty':>5} {'Price':>10} {'Total':>10}")
        lines.append("-" * 40)

        for item in invoice.items:
            price = Decimal(item.unit_price_cents) / 100
            total = Decimal(item.total_cents) / 100
            lines.append(
                f"{item.description[:30]:<30} {item.quantity:>5} "
                f"{invoice.currency} {price:>7.2f} {invoice.currency} {total:>7.2f}"
            )

        lines.append("-" * 40)

        # Totals
        lines.append(f"{'Subtotal:':<45} {invoice.currency} {invoice.subtotal:>10.2f}")
        lines.append(f"{'Tax (' + str(invoice.tax_rate_percent) + '%):':<45} {invoice.currency} {invoice.tax:>10.2f}")
        lines.append("=" * 60)
        lines.append(f"{'TOTAL:':<45} {invoice.currency} {invoice.total:>10.2f}")
        lines.append("=" * 60)

        # Payment info
        if invoice.is_paid:
            lines.append("")
            lines.append(f"PAID on {invoice.paid_at.strftime('%Y-%m-%d') if invoice.paid_at else 'N/A'}")
            if invoice.payment_method:
                lines.append(f"Payment Method: {invoice.payment_method}")
            if invoice.payment_reference:
                lines.append(f"Reference: {invoice.payment_reference}")

        # Notes
        if invoice.notes:
            lines.append("")
            lines.append("Notes:")
            lines.append(invoice.notes)

        # Footer
        lines.append("")
        lines.append("-" * 60)
        lines.append("Thank you for your business!")
        lines.append("")

        content = "\n".join(lines)
        return content.encode("utf-8")

    def format_amount(
        self,
        cents: int,
        currency: str = "EUR",
    ) -> str:
        """
        Format amount for display.

        Args:
            cents: Amount in cents
            currency: Currency code

        Returns:
            Formatted amount string
        """
        amount = Decimal(cents) / 100
        if currency == "EUR":
            return f"€{amount:,.2f}"
        elif currency == "USD":
            return f"${amount:,.2f}"
        else:
            return f"{currency} {amount:,.2f}"


# Global invoice service instance
_invoice_service: InvoiceService | None = None


def get_invoice_service() -> InvoiceService:
    """Get the global invoice service instance."""
    global _invoice_service
    if _invoice_service is None:
        _invoice_service = InvoiceService()
    return _invoice_service


def configure_invoice_service(config: InvoiceConfig) -> InvoiceService:
    """Configure and return the global invoice service."""
    global _invoice_service
    _invoice_service = InvoiceService(config=config)
    return _invoice_service
