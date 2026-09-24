from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from invoice_app.models.invoice import Invoice
from invoice_app.models.invoice_item import InvoiceItem
from invoice_app.services import invoice_service, pdf_service
from invoice_app.services.invoice_service import InvoiceValidationError, normalize_service_period


DAY = date(2026, 9, 24)
VALID_PERIODS = [
    ({"service_period_mode": "none", "service_date_from": None, "service_date_to": None}, None),
    ({"service_period_mode": "single", "service_date_from": DAY, "service_date_to": None}, "24.09.2026"),
    ({"service_period_mode": "range", "service_date_from": date(2026, 9, 1), "service_date_to": date(2026, 9, 30)}, "01.09.2026 - 30.09.2026"),
    ({"service_period_mode": "range", "service_date_from": DAY, "service_date_to": DAY}, "24.09.2026 - 24.09.2026"),
    ({"service_period": "September 2026"}, "September 2026"),
    ({"service_period": None}, None),
    ({}, None),
    ({"service_period_mode": "none", "service_period": "September 2026"}, None),
    ({"service_period_mode": "single", "service_date_from": DAY, "service_period": "Alt"}, "24.09.2026"),
    ({"service_period_mode": "single", "service_date_from": date(2099, 1, 1)}, "01.01.2099"),
    ({"service_period_mode": "single", "service_date_from": date(999, 1, 1)}, "01.01.0999"),
]
INVALID_PERIODS = [
    ({"service_period_mode": "range", "service_date_from": DAY, "service_date_to": date(2026, 9, 1)}, "service_date_to"),
    ({"service_period_mode": "single"}, "service_date_from"),
    ({"service_period_mode": "range", "service_date_to": DAY}, "service_date_from"),
    ({"service_period_mode": "range", "service_date_from": DAY}, "service_date_to"),
    ({"service_period_mode": "invalid"}, "service_period_mode"),
    ({"service_period_mode": None}, "service_period_mode"),
    ({"service_period_mode": "single", "service_date_from": "24.09.2026"}, "service_date_from"),
    ({"service_period_mode": "single", "service_date_from": datetime(2026, 9, 24)}, "service_date_from"),
    ({"service_period_mode": "range", "service_date_from": DAY, "service_date_to": "30.09.2026"}, "service_date_to"),
    ({"service_period_mode": "single", "service_date_from": DAY, "service_date_to": DAY}, "service_date_to"),
    ({"service_period_mode": "none", "service_date_from": DAY}, "service_period_mode"),
    ({"service_period_mode": "none", "service_date_to": DAY}, "service_period_mode"),
    ({"service_period_mode": "single", "service_period": "Kein Fallback"}, "service_date_from"),
    ({"service_period": DAY}, "service_period_mode"),
]


@pytest.mark.parametrize("data, expected", VALID_PERIODS)
def test_normalize_service_period_compatible_and_non_mutating(data, expected):
    before = deepcopy(data)
    assert normalize_service_period(data) == expected
    assert data == before


@pytest.mark.parametrize("data, field", INVALID_PERIODS)
def test_normalize_service_period_rejects_invalid_values(data, field):
    before = deepcopy(data)
    with pytest.raises(InvoiceValidationError) as error:
        normalize_service_period(data)
    assert error.value.field == field
    assert data == before


@pytest.mark.parametrize("invalid, field", INVALID_PERIODS + [
    ({"customer_id": None}, "customer_id"),
    ({"invoice_date": None}, "invoice_date"),
    ({"invoice_date": "24.09.2026"}, "invoice_date"),
    ({"due_date": "08.10.2026"}, "due_date"),
    ({"items": []}, "items"),
])
def test_invalid_creation_does_not_access_database_or_exports(
    invoice_environment, invoice_payload, monkeypatch, invalid, field
):
    service = invoice_environment.service
    session_factory = Mock(side_effect=AssertionError("DB must not be accessed"))
    monkeypatch.setattr(invoice_service, "SessionLocal", session_factory)
    json_export = Mock()
    pdf_export = Mock()
    monkeypatch.setattr(service.json_service, "write_invoice_json", json_export)
    monkeypatch.setattr(service.pdf_service, "create_invoice_pdf", pdf_export)
    with pytest.raises(InvoiceValidationError) as error:
        service.create_invoice({**invoice_payload, **invalid})
    assert error.value.field == field
    session_factory.assert_not_called()
    json_export.assert_not_called()
    pdf_export.assert_not_called()
    with invoice_environment.sessions() as session:
        assert session.scalar(select(func.count(Invoice.id))) == 0


@pytest.mark.parametrize("period, expected", VALID_PERIODS)
def test_real_creation_has_same_service_period_in_database_json_pdf(
    invoice_environment, invoice_payload, monkeypatch, period, expected
):
    drawn = []
    real_canvas = pdf_service.canvas.Canvas

    def canvas_spy(*args, **kwargs):
        canvas = real_canvas(*args, **kwargs)
        original_draw = canvas.drawString

        def draw(x, y, text, *args, **kwargs):
            drawn.append((y, text))
            return original_draw(x, y, text, *args, **kwargs)

        canvas.drawString = draw
        return canvas

    monkeypatch.setattr(pdf_service.canvas, "Canvas", canvas_spy)
    payload = {**invoice_payload, **period}
    before = deepcopy(payload)
    result = invoice_environment.service.create_invoice(payload)
    assert payload == before
    with invoice_environment.sessions() as session:
        invoice = session.get(Invoice, result.id)
        assert invoice.service_period == expected
        assert invoice.gross_total == Decimal("119.00")
        assert invoice.status == "offen"
        assert len(invoice.items) == 1
    json_data = json.loads(Path(result.json_path).read_text())
    assert json_data["service_period"] == expected
    assert json_data["invoice_date"] == "2026-09-24"
    assert json_data["due_date"] == "2026-10-08"
    assert Path(result.pdf_path).read_bytes().startswith(b"%PDF-")
    assert [text for _, text in drawn if text.startswith("Leistung:")] == (
        [f"Leistung: {expected}"] if expected else []
    )
    # All existing content still renders below the preceding line, not over it.
    assert all(a[0] > b[0] for a, b in zip(drawn, drawn[1:]))
    assert any(text.startswith("Brutto:") for _, text in drawn)
    assert any(text.startswith("Zahlungsziel:") for _, text in drawn)


@pytest.mark.parametrize("failure_stage", ["json", "pdf", "commit"])
def test_failure_before_commit_rolls_back_and_allows_one_retry(
    invoice_environment, invoice_payload, monkeypatch, failure_stage
):
    service = invoice_environment.service
    existing = service.create_invoice(invoice_payload)
    existing_files = {p: Path(p).read_bytes() for p in [existing.json_path, existing.pdf_path]}

    def fail(*args, **kwargs):
        raise OSError("simulierter Schreibfehler")

    def fail_commit(session):
        session.flush()
        raise OSError("simulierter Schreibfehler vor Commit")

    with monkeypatch.context() as patch:
        if failure_stage == "commit":
            patch.setattr(Session, "commit", fail_commit)
        else:
            target, method = ((service.json_service, "write_invoice_json") if failure_stage == "json"
                              else (service.pdf_service, "create_invoice_pdf"))
            patch.setattr(target, method, fail)
        with pytest.raises(OSError, match="Schreibfehler"):
            service.create_invoice(invoice_payload)
    with invoice_environment.sessions() as session:
        assert session.scalar(select(func.count(Invoice.id))) == 1
        assert session.scalar(select(func.count(InvoiceItem.id))) == 1
    result = service.create_invoice(invoice_payload)
    assert result.number == "2026-0002"
    with invoice_environment.sessions() as session:
        assert session.scalar(select(func.count(Invoice.id))) == 2
        assert session.scalar(select(func.count(InvoiceItem.id))) == 2
    assert {p: Path(p).read_bytes() for p in existing_files} == existing_files


def test_success_never_refreshes_after_commit_and_returns_loaded_values(
    invoice_environment, invoice_payload, monkeypatch
):
    refresh = Mock(side_effect=OSError("Refresh nach Commit darf nicht stattfinden"))
    monkeypatch.setattr(Session, "refresh", refresh)
    result = invoice_environment.service.create_invoice(invoice_payload)
    assert result.id is not None
    assert result.number == "2026-0001"
    assert result.gross_total == 119
    assert result.pdf_path and result.json_path
    refresh.assert_not_called()
    with invoice_environment.sessions() as session:
        assert session.expire_on_commit is True
        assert session.scalar(select(func.count(Invoice.id))) == 1


def test_unknown_customer_is_field_error_without_exports(invoice_environment, invoice_payload, monkeypatch):
    service = invoice_environment.service
    json_export = Mock()
    pdf_export = Mock()
    monkeypatch.setattr(service.json_service, "write_invoice_json", json_export)
    monkeypatch.setattr(service.pdf_service, "create_invoice_pdf", pdf_export)
    with pytest.raises(InvoiceValidationError) as error:
        service.create_invoice({**invoice_payload, "customer_id": 99999})
    assert error.value.field == "customer_id"
    json_export.assert_not_called()
    pdf_export.assert_not_called()
    with invoice_environment.sessions() as session:
        assert session.scalar(select(func.count(Invoice.id))) == 0
