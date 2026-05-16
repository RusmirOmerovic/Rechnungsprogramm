from datetime import date
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

    def create_invoice(self, data: dict) -> Invoice:
        invoice = Invoice(**data)
        self.session.add(invoice)
        self.session.flush()
        return invoice

    def get_invoice(self, invoice_id: int) -> Invoice | None:
        return self.session.get(Invoice, invoice_id)
