from invoice_app.services.invoice_service import InvoiceService
import pytest


def test_positionsberechnung():
    service = InvoiceService()
    item = service.calculate_item({"description": "Test", "quantity": 2, "unit": "h", "unit_price_net": 50, "tax_rate": 19})
    assert item["line_net"] == 100.00
    assert item["line_tax"] == 19.00
    assert item["line_gross"] == 119.00


def test_rechnungssummen():
    service = InvoiceService()
    totals = service.calculate_totals([
        {"description": "A", "quantity": 2, "unit": "h", "unit_price_net": 10, "tax_rate": 10},
        {"description": "B", "quantity": 1, "unit": "h", "unit_price_net": 20, "tax_rate": 20},
    ])
    assert totals["net_total"] == 40.00
    assert totals["tax_total"] == 6.00
    assert totals["gross_total"] == 46.00


def test_ungueltige_menge():
    service = InvoiceService()
    with pytest.raises(ValueError):
        service.calculate_item({"description": "X", "quantity": 0, "unit": "", "unit_price_net": 10, "tax_rate": 19})


def test_rechnung_ohne_position_abgelehnt():
    service = InvoiceService()
    with pytest.raises(ValueError):
        service.create_invoice({"customer_id": 1, "invoice_date": None, "items": []})
