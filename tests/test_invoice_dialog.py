from copy import deepcopy
from datetime import date
import os
from unittest.mock import Mock

import pytest
from sqlalchemy import func, select

# The ordinary pytest command also works on CI without a display server.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QDate, Qt, QTimer
from PySide6.QtGui import QColor, QPalette
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QFrame, QMessageBox

from invoice_app.dialogs.invoice_dialog import InvoiceDialog
from invoice_app.models.invoice import Invoice
from invoice_app.pages.invoices_page import InvoicesPage


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def dialog(app, invoice_environment):
    widget = InvoiceDialog()
    widget.show()
    app.processEvents()
    yield widget
    widget.close()
    widget.deleteLater()
    app.processEvents()


def fill_form(dialog, with_item=True):
    dialog.invoice_date.setDate(QDate(2026, 9, 24))
    dialog.due_date.setDate(QDate(2026, 10, 8))
    dialog.status.setText("offen")
    dialog.desc.setText("Arbeit")
    dialog.qty.setText("2")
    dialog.unit.setText("h")
    dialog.price.setText("50")
    dialog.tax.setText("19")
    if with_item:
        dialog.add_item()
        # Draft fields which have NOT been added must survive errors as well.
        dialog.desc.setText("Noch nicht hinzugefügt")
        dialog.qty.setText("3")
        dialog.unit.setText("Stk")
        dialog.price.setText("25")
        dialog.tax.setText("7")


def snapshot(dialog):
    return deepcopy((dialog.get_data(), [field.text() for field in (
        dialog.desc, dialog.qty, dialog.unit, dialog.price, dialog.tax
    )]))


def count_invoices(environment):
    with environment.sessions() as session:
        return session.scalar(select(func.count(Invoice.id)))


def test_missing_customer_preserves_everything_then_creates_exactly_once(
    app, dialog, invoice_environment, monkeypatch
):
    assert dialog.customer_combo.count() == 2  # one customer is not auto-selected
    assert dialog.customer_combo.currentData() is None
    assert dialog.customer_combo.currentText() == "Bitte Kunden auswählen"
    fill_form(dialog)
    before = snapshot(dialog)
    create = Mock(wraps=dialog.invoice_service.create_invoice)
    monkeypatch.setattr(dialog.invoice_service, "create_invoice", create)
    dialog.save_button.click()
    assert dialog.isVisible()
    assert dialog.result() != QDialog.DialogCode.Accepted
    assert snapshot(dialog) == before
    assert dialog.customer_error.isVisible()
    assert dialog.customer_error.text()
    assert dialog.customer_combo.hasFocus()
    assert dialog.customer_field.frameShape() == QFrame.Shape.Box
    assert count_invoices(invoice_environment) == 0
    dialog.customer_combo.setCurrentIndex(1)
    assert not dialog.customer_error.isVisible()
    assert dialog.customer_field.frameShape() == QFrame.Shape.NoFrame
    dialog.save_button.click()
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert not dialog.isVisible()
    assert count_invoices(invoice_environment) == 1
    dialog.accept()
    dialog.save_button.click()
    assert create.call_count == 2  # rejected attempt + exactly one successful call
    assert count_invoices(invoice_environment) == 1


def test_missing_items_with_valid_customer_and_date_stays_open(dialog, invoice_environment):
    fill_form(dialog, with_item=False)
    dialog.customer_combo.setCurrentIndex(1)
    before = snapshot(dialog)
    dialog.accept()
    assert dialog.isVisible()
    assert snapshot(dialog) == before
    assert "Position" in dialog.save_error.text()
    assert dialog.desc.hasFocus()
    assert count_invoices(invoice_environment) == 0
    dialog.add_item()
    dialog.accept()
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert count_invoices(invoice_environment) == 1


def test_customer_error_follows_theme_palette(app, dialog):
    dialog.accept()
    original_palette = app.palette()
    try:
        for background, foreground in [("#202124", "#f1f3f4"), ("#ffffff", "#202124")]:
            palette = QPalette(original_palette)
            palette.setColor(QPalette.ColorRole.Window, QColor(background))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(foreground))
            palette.setColor(QPalette.ColorRole.Text, QColor(foreground))
            app.setPalette(palette)
            app.processEvents()
            assert dialog.customer_error.palette().color(QPalette.ColorRole.WindowText) == QColor(foreground)
            assert dialog.customer_combo.palette().color(QPalette.ColorRole.Text) == QColor(foreground)
            assert dialog.customer_error.isVisible()
    finally:
        app.setPalette(original_palette)
        app.processEvents()


def test_technical_export_failure_preserves_dialog_and_retry_succeeds(
    dialog, invoice_environment, monkeypatch
):
    fill_form(dialog)
    dialog.customer_combo.setCurrentIndex(1)
    before = snapshot(dialog)
    with monkeypatch.context() as patch:
        patch.setattr(dialog.invoice_service.pdf_service, "create_invoice_pdf",
                      Mock(side_effect=OSError("temporärer PDF-Fehler")))
        dialog.accept()
    assert dialog.isVisible()
    assert snapshot(dialog) == before
    assert "temporärer PDF-Fehler" in dialog.save_error.text()
    assert dialog.save_button.isEnabled()
    assert count_invoices(invoice_environment) == 0
    dialog.accept()
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert count_invoices(invoice_environment) == 1


def test_reentrant_accept_and_enter_share_guarded_save_path(dialog, invoice_environment, monkeypatch):
    fill_form(dialog)
    dialog.customer_combo.setCurrentIndex(1)
    real_create = dialog.invoice_service.create_invoice

    def reentrant_create(data):
        assert not dialog.save_button.isEnabled()
        dialog.accept()  # an accidental re-entry must not create again
        return real_create(data)

    create = Mock(side_effect=reentrant_create)
    monkeypatch.setattr(dialog.invoice_service, "create_invoice", create)
    dialog.status.setFocus()
    QTest.keyClick(dialog.status, Qt.Key.Key_Return)
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert create.call_count == 1
    assert count_invoices(invoice_environment) == 1


@pytest.mark.parametrize("action", ["button", "escape", "close"])
def test_explicit_cancel_never_saves(dialog, invoice_environment, monkeypatch, action):
    fill_form(dialog)
    dialog.customer_combo.setCurrentIndex(1)
    create = Mock()
    monkeypatch.setattr(dialog.invoice_service, "create_invoice", create)
    if action == "button":
        dialog.cancel_button.click()
    elif action == "escape":
        QTest.keyClick(dialog, Qt.Key.Key_Escape)
    else:
        dialog.close()
    assert dialog.result() == QDialog.DialogCode.Rejected
    assert not dialog.isVisible()
    create.assert_not_called()
    assert count_invoices(invoice_environment) == 0


def test_calendar_modes_only_submit_active_dates_and_preserve_other_inputs(dialog):
    fill_form(dialog)
    original, drafts = snapshot(dialog)
    assert original["service_period_mode"] == "none"
    assert original["service_date_from"] is original["service_date_to"] is None
    assert not dialog.service_dates.isVisible()
    for field in (dialog.service_date_from, dialog.service_date_to):
        assert field.calendarPopup()
        assert field.displayFormat() == "dd.MM.yyyy"
    dialog.service_date_from.setDate(QDate(2026, 9, 1))
    dialog.service_date_to.setDate(QDate(2026, 9, 30))
    for mode in ("range", "single", "none", "range"):
        dialog.service_period_mode.setCurrentIndex(dialog.service_period_mode.findData(mode))
        payload = dialog.get_data()
        assert payload["service_date_from"] == (date(2026, 9, 1) if mode != "none" else None)
        assert payload["service_date_to"] == (date(2026, 9, 30) if mode == "range" else None)
        assert dialog.service_date_to.isVisible() == (mode == "range")
        assert dialog.service_date_to.isEnabled() == (mode == "range")
        assert snapshot(dialog)[1] == drafts
        for key in ("customer_id", "invoice_date", "due_date", "status", "items"):
            assert payload[key] == original[key]


def test_reversed_range_keeps_values_and_focuses_end_date(dialog, invoice_environment):
    fill_form(dialog)
    dialog.customer_combo.setCurrentIndex(1)
    dialog.service_period_mode.setCurrentIndex(2)
    dialog.service_date_from.setDate(QDate(2026, 9, 30))
    dialog.service_date_to.setDate(QDate(2026, 9, 1))
    before = snapshot(dialog)
    dialog.accept()
    assert dialog.isVisible()
    assert snapshot(dialog) == before
    assert dialog.service_date_to.hasFocus()
    assert "Bis-Datum" in dialog.save_error.text()
    assert count_invoices(invoice_environment) == 0


@pytest.mark.parametrize("refresh_fails", [False, True])
def test_page_only_refreshes_after_dialog_save(app, invoice_environment, monkeypatch, refresh_fails):
    page = InvoicesPage()
    page_create = Mock(side_effect=AssertionError("Page must not create"))
    monkeypatch.setattr(page.service, "create_invoice", page_create)
    refresh = Mock(side_effect=OSError("Listenfehler") if refresh_fails else None)
    monkeypatch.setattr(page, "load_invoices", refresh)
    warning = Mock()
    monkeypatch.setattr(QMessageBox, "warning", warning)
    real_exec = InvoiceDialog.exec
    accepted_dialogs = []

    def exec_and_save(dialog):
        fill_form(dialog)
        dialog.customer_combo.setCurrentIndex(1)
        QTimer.singleShot(0, dialog.accept)
        result = real_exec(dialog)
        accepted_dialogs.append(dialog)
        return result

    monkeypatch.setattr(InvoiceDialog, "exec", exec_and_save)
    page.create_invoice()
    assert len(accepted_dialogs) == 1
    assert accepted_dialogs[0].result() == QDialog.DialogCode.Accepted
    assert count_invoices(invoice_environment) == 1
    page_create.assert_not_called()
    refresh.assert_called_once()
    if refresh_fails:
        assert "wurde gespeichert" in warning.call_args.args[2]
        assert "nicht die Rechnung erneut erstellen" in warning.call_args.args[2]
    else:
        warning.assert_not_called()
    page.close()
    page.deleteLater()
    app.processEvents()


def test_page_does_not_refresh_or_create_on_cancel(app, invoice_environment, monkeypatch):
    page = InvoicesPage()
    create = Mock()
    refresh = Mock()
    monkeypatch.setattr(page.service, "create_invoice", create)
    monkeypatch.setattr(page, "load_invoices", refresh)
    monkeypatch.setattr(InvoiceDialog, "exec", lambda self: QDialog.DialogCode.Rejected)
    page.create_invoice()
    create.assert_not_called()
    refresh.assert_not_called()
    page.close()
    page.deleteLater()
    app.processEvents()
