from decimal import Decimal

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from invoice_app.services.dashboard_service import DashboardService


class DashboardPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.service = DashboardService()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Überblick</h2>"))

        metrics = QFormLayout()
        self.customer_count_label = QLabel()
        self.invoice_count_label = QLabel()
        self.gross_total_label = QLabel()
        self.open_gross_total_label = QLabel()
        metrics.addRow("Kunden", self.customer_count_label)
        metrics.addRow("Rechnungen", self.invoice_count_label)
        metrics.addRow("Gesamtumsatz", self.gross_total_label)
        metrics.addRow("Offene Rechnungen", self.open_gross_total_label)
        layout.addLayout(metrics)

        layout.addWidget(QLabel("<h3>Letzte Rechnungen</h3>"))
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Rechnungsnummer", "Kunde", "Datum", "Brutto", "Status"
        ])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.refresh_button = QPushButton("Aktualisieren")
        self.refresh_button.clicked.connect(self.load_dashboard)
        layout.addWidget(self.refresh_button)

    @staticmethod
    def _format_amount(amount: Decimal) -> str:
        return f"{amount:,.2f}".translate(str.maketrans(",.", ".,")) + " €"

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.load_dashboard()

    def load_dashboard(self) -> None:
        try:
            data = self.service.get_dashboard()
        except Exception as error:
            for label in (
                self.customer_count_label, self.invoice_count_label,
                self.gross_total_label, self.open_gross_total_label,
            ):
                label.setText("–")
            self.table.setRowCount(0)
            QMessageBox.critical(self, "Fehler", f"Dashboard konnte nicht geladen werden:\n{error}")
            return

        self.customer_count_label.setText(str(data.customer_count))
        self.invoice_count_label.setText(str(data.invoice_count))
        self.gross_total_label.setText(self._format_amount(data.gross_total))
        self.open_gross_total_label.setText(self._format_amount(data.open_gross_total))
        self.table.setRowCount(len(data.recent_invoices))
        for row, invoice in enumerate(data.recent_invoices):
            values = [
                invoice.number,
                invoice.customer.name if invoice.customer else "–",
                invoice.invoice_date.strftime("%d.%m.%Y"),
                self._format_amount(invoice.gross_total),
                invoice.status,
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))
        self.table.resizeColumnsToContents()
