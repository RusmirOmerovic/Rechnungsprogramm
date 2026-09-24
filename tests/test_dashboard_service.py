from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from invoice_app.database.base import Base
from invoice_app.models.customer import Customer
from invoice_app.models.invoice import Invoice
from invoice_app.repositories.invoice_repository import InvoiceRepository
from invoice_app.services import dashboard_service


@pytest.fixture
def database(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'dashboard.db'}")
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    monkeypatch.setattr(dashboard_service, "SessionLocal", sessions)
    yield sessions
    engine.dispose()


def add_invoices(database, amounts, statuses=None, created_at=None):
    with database() as session:
        customer = Customer(customer_number="K-1", name="Testkunde")
        session.add(customer)
        session.flush()
        for index, amount in enumerate(amounts):
            session.add(Invoice(
                number=f"2026-{index + 1:04d}",
                customer_id=customer.id,
                invoice_date=date(2026, 1, 1),
                # Deliberately unrelated to gross: the dashboard must use stored gross.
                net_total=Decimal("999.00"),
                tax_total=Decimal("111.00"),
                gross_total=Decimal(amount),
                status=statuses[index] if statuses else "erstellt",
                created_at=created_at[index] if created_at else datetime(2026, 1, 1),
            ))
        session.commit()


def test_empty_database_returns_zero_dashboard_values(database):
    result = dashboard_service.DashboardService().get_dashboard()
    assert result.customer_count == 0
    assert result.invoice_count == 0
    assert result.gross_total == Decimal("0.00")
    assert result.open_gross_total == Decimal("0.00")
    assert result.recent_invoices == []


def test_customer_count_uses_persisted_customers(database):
    with database() as session:
        session.add_all([
            Customer(customer_number="K-1", name="A"),
            Customer(customer_number="K-2", name="B"),
        ])
        session.commit()
    assert dashboard_service.DashboardService().get_dashboard().customer_count == 2


def test_invoice_count_includes_all_statuses(database):
    add_invoices(database, ["10", "20", "30"], ["offen", "erstellt", "bezahlt"])
    assert dashboard_service.DashboardService().get_dashboard().invoice_count == 3


def test_gross_total_uses_persisted_gross_with_decimal_cents(database):
    add_invoices(database, ["0.10", "0.20", "119.99"])
    assert dashboard_service.DashboardService().get_dashboard().gross_total == Decimal("120.29")


def test_open_gross_total_matches_only_exact_status(database):
    add_invoices(
        database, ["10.01", "20.02", "30", "40", "50", "60", "70"],
        ["offen", "offen", "Offen", "offen ", "erstellt", "bezahlt", "archiviert"],
    )
    assert dashboard_service.DashboardService().get_dashboard().open_gross_total == Decimal("30.03")


def test_no_open_invoices_returns_zero(database):
    add_invoices(database, ["119.00"])
    assert dashboard_service.DashboardService().get_dashboard().open_gross_total == Decimal("0.00")


def test_recent_invoices_limited_and_ordered_with_customers_loaded(database):
    start = datetime(2026, 1, 1)
    add_invoices(database, ["1"] * 7, created_at=[
        start + timedelta(days=days) for days in [2, 5, 1, 5, 0, 4, 3]
    ])
    result = dashboard_service.DashboardService().get_dashboard()
    assert [invoice.number for invoice in result.recent_invoices] == [
        "2026-0004", "2026-0002", "2026-0006", "2026-0007", "2026-0001"
    ]
    # The service session is closed; rendering must not trigger lazy loading.
    assert all(invoice.customer.name == "Testkunde" for invoice in result.recent_invoices)
    assert result.invoice_count == 7
    assert result.gross_total == Decimal("7.00")


def test_repository_recent_limit(database):
    add_invoices(database, ["1", "2", "3"])
    with database() as session:
        repo = InvoiceRepository(session)
        assert len(repo.list_recent_invoices(2)) == 2
        assert repo.list_recent_invoices(0) == []
        with pytest.raises(ValueError, match="Limit"):
            repo.list_recent_invoices(-1)


def test_dashboard_reload_reads_new_committed_data(database):
    service = dashboard_service.DashboardService()
    assert service.get_dashboard().invoice_count == 0
    add_invoices(database, ["12.34"], ["offen"])
    result = service.get_dashboard()
    assert result.customer_count == 1
    assert result.invoice_count == 1
    assert result.open_gross_total == Decimal("12.34")
    assert len(result.recent_invoices) == 1
