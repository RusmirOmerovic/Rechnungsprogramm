from datetime import date
from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from invoice_app.models.invoice import Invoice


class InvoiceRepository:
    def __init__(self, session) -> None:
        self.session = session

    def list_invoices(self) -> list[Invoice]:
        stmt = select(Invoice).options(joinedload(Invoice.customer)).order_by(Invoice.id.desc())
        return list(self.session.scalars(stmt).unique().all())

    def get_last_number_for_year(self, year: int) -> str | None:
        prefix = f"{year}-%"
        stmt = select(func.max(Invoice.number)).where(Invoice.number.like(prefix))
        return self.session.scalar(stmt)

    def count_invoices(self) -> int:
        return self.session.scalar(select(func.count(Invoice.id)))

    def sum_gross_total(self) -> Decimal:
        total = self.session.scalar(select(func.sum(Invoice.gross_total)))
        return total if total is not None else Decimal("0.00")

    def sum_gross_total_by_status(self, status: str) -> Decimal:
        stmt = select(func.sum(Invoice.gross_total)).where(Invoice.status == status)
        total = self.session.scalar(stmt)
        return total if total is not None else Decimal("0.00")

    def list_recent_invoices(self, limit: int) -> list[Invoice]:
        if limit < 0:
            raise ValueError("Limit darf nicht negativ sein.")
        stmt = (
            select(Invoice)
            .options(joinedload(Invoice.customer))
            .order_by(Invoice.created_at.desc(), Invoice.id.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt).unique().all())

    def create_invoice(self, data: dict) -> Invoice:
        invoice = Invoice(**data)
        self.session.add(invoice)
        self.session.flush()
        return invoice

    def get_invoice(self, invoice_id: int) -> Invoice | None:
        return self.session.get(Invoice, invoice_id)
