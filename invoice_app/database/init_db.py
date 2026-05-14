from invoice_app.database.base import Base
from invoice_app.database.session import engine
from invoice_app.models.app_settings import AppSettings
from invoice_app.models.customer import Customer
from invoice_app.models.invoice import Invoice
from invoice_app.models.invoice_item import InvoiceItem


def init_database() -> None:
    # Imports above ensure all models are registered in metadata.
    _ = (AppSettings, Customer, Invoice, InvoiceItem)
    Base.metadata.create_all(bind=engine)
