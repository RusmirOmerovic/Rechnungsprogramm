import os
import subprocess
from PySide6.QtWidgets import QHBoxLayout, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from invoice_app.dialogs.invoice_dialog import InvoiceDialog
from invoice_app.services.invoice_service import InvoiceService


class InvoicesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = InvoiceService()
        self.invoices = []
        root = QVBoxLayout(self)
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["ID", "Rechnungsnummer", "Kunde", "Datum", "Netto", "Steuer", "Brutto", "Status"])
        root.addWidget(self.table)
        buttons = QHBoxLayout()
        self.new_button = QPushButton("Neue Rechnung"); self.open_pdf_button = QPushButton("PDF öffnen")
        self.archive_button = QPushButton("Archivieren"); self.refresh_button = QPushButton("Aktualisieren")
        for b in [self.new_button, self.open_pdf_button, self.archive_button, self.refresh_button]: buttons.addWidget(b)
        buttons.addStretch(1); root.addLayout(buttons)
        self.new_button.clicked.connect(self.create_invoice); self.open_pdf_button.clicked.connect(self.open_pdf)
        self.archive_button.clicked.connect(self.archive_invoice); self.refresh_button.clicked.connect(self.load_invoices)
        self.load_invoices()

    def load_invoices(self):
        self.invoices = self.service.list_invoices()
        self.table.setRowCount(len(self.invoices))
        for r, inv in enumerate(self.invoices):
            vals=[inv.id, inv.number, inv.customer.name if inv.customer else "-", inv.invoice_date, inv.net_total, inv.tax_total, inv.gross_total, inv.status]
            for c,v in enumerate(vals): self.table.setItem(r,c,QTableWidgetItem(str(v)))

    def _selected(self):
        row = self.table.currentRow()
        return self.invoices[row] if 0 <= row < len(self.invoices) else None

    def create_invoice(self):
        dialog = InvoiceDialog(self)
        if not dialog.exec(): return
        try:
            self.service.create_invoice(dialog.get_data()); self.load_invoices()
        except Exception as e:
            QMessageBox.warning(self,"Fehler",str(e))

    def open_pdf(self):
        inv = self._selected()
        if not inv or not inv.pdf_path: return
        subprocess.Popen(["xdg-open", inv.pdf_path])

    def archive_invoice(self):
        inv = self._selected()
        if not inv: return
        inv.status = "archiviert"
        QMessageBox.information(self, "Hinweis", "Status auf 'archiviert' gesetzt. Bitte Aktualisieren/Speichern in nächster Phase persistieren.")
