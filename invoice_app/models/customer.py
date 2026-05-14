from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from invoice_app.database.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    invoices = relationship("Invoice", back_populates="customer", cascade="all, delete-orphan")
