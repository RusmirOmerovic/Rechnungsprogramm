from dataclasses import dataclass
from decimal import Decimal

from invoice_app.database.session import SessionLocal
from invoice_app.models.invoice import Invoice
from invoice_app.repositories.customer_repository import CustomerRepository
from invoice_app.repositories.invoice_repository import InvoiceRepository


@dataclass(frozen=True)
class DashboardResult:
    customer_count: int
    invoice_count: int
    gross_total: Decimal
    open_gross_total: Decimal
    recent_invoices: list[Invoice]


class DashboardService:
    def get_dashboard(self) -> DashboardResult:
        with SessionLocal() as session:
            customers = CustomerRepository(session)
            invoices = InvoiceRepository(session)
            return DashboardResult(
                customer_count=customers.count_customers(),
                invoice_count=invoices.count_invoices(),
                gross_total=invoices.sum_gross_total(),
                open_gross_total=invoices.sum_gross_total_by_status("offen"),
                recent_invoices=invoices.list_recent_invoices(limit=5),
            )
