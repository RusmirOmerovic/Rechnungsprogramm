from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from invoice_app.database.base import Base


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=1)
    unit: Mapped[str | None] = mapped_column(String(30), nullable=True)
    unit_price_net: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=19)
    line_net: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    line_tax: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    line_gross: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    invoice = relationship("Invoice", back_populates="items")
