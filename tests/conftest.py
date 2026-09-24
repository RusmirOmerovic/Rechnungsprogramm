from datetime import date
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from invoice_app.database.base import Base
from invoice_app.models.customer import Customer
from invoice_app.services import customer_service, invoice_service
from invoice_app.services.json_service import JsonService
from invoice_app.services.pdf_service import PdfService


@pytest.fixture
def invoice_environment(tmp_path, monkeypatch):
    """Opt-in isolation for new creation/dialog tests; never use project data."""
    engine = create_engine(f"sqlite:///{tmp_path / 'invoices.db'}")
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine, autoflush=False)
    monkeypatch.setattr(invoice_service, "SessionLocal", sessions)
    monkeypatch.setattr(customer_service, "SessionLocal", sessions)

    def json_init(self):
        self.base_dir = tmp_path / "json"
        self.base_dir.mkdir(exist_ok=True)

    def pdf_init(self):
        self.base_dir = tmp_path / "pdf"
        self.base_dir.mkdir(exist_ok=True)

    monkeypatch.setattr(JsonService, "__init__", json_init)
    monkeypatch.setattr(PdfService, "__init__", pdf_init)
    with sessions() as session:
        customer = Customer(customer_number="K-1", name="Testkunde", street="Testweg 1",
                            postal_code="12345", city="Teststadt")
        session.add(customer)
        session.flush()
        customer_id = customer.id
        session.commit()
    yield SimpleNamespace(sessions=sessions, service=invoice_service.InvoiceService(),
                          customer_id=customer_id, path=tmp_path)
    engine.dispose()


@pytest.fixture
def invoice_payload(invoice_environment):
    return {
        "customer_id": invoice_environment.customer_id,
        "invoice_date": date(2026, 9, 24),
        "due_date": date(2026, 10, 8),
        "status": "offen",
        "items": [{"description": "Arbeit", "quantity": 2, "unit": "h",
                   "unit_price_net": 50, "tax_rate": 19}],
    }
