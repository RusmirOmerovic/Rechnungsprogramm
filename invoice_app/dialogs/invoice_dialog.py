from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QFormLayout, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout
)

from invoice_app.services.customer_service import CustomerService
from invoice_app.services.invoice_service import InvoiceService


class InvoiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neue Rechnung")
        self.resize(900, 650)
        self.customer_service = CustomerService()
        self.invoice_service = InvoiceService()
        self.items = []

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.customer_combo = QComboBox()
        self.invoice_date = QDateEdit(QDate.currentDate()); self.invoice_date.setCalendarPopup(True)
        self.service_period = QLineEdit()
        self.due_date = QDateEdit(QDate.currentDate()); self.due_date.setCalendarPopup(True)
        self.status = QLineEdit("erstellt")
        form.addRow("Kunde", self.customer_combo)
        form.addRow("Rechnungsdatum", self.invoice_date)
        form.addRow("Leistungszeitraum", self.service_period)
        form.addRow("Zahlungsziel", self.due_date)
        form.addRow("Status", self.status)
        layout.addLayout(form)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["Beschreibung", "Menge", "Einheit", "Einzelpreis netto", "Steuersatz", "Netto", "Steuer", "Brutto"])
        layout.addWidget(self.table)

        grid = QGridLayout()
        self.desc = QLineEdit(); self.qty = QLineEdit("1"); self.unit = QLineEdit("Stk")
        self.price = QLineEdit("0"); self.tax = QLineEdit("19")
        add = QPushButton("Position hinzufügen"); delete = QPushButton("Position löschen")
        grid.addWidget(QLabel("Beschreibung"),0,0); grid.addWidget(self.desc,0,1)
        grid.addWidget(QLabel("Menge"),0,2); grid.addWidget(self.qty,0,3)
        grid.addWidget(QLabel("Einheit"),1,0); grid.addWidget(self.unit,1,1)
        grid.addWidget(QLabel("Einzelpreis netto"),1,2); grid.addWidget(self.price,1,3)
        grid.addWidget(QLabel("Steuersatz"),2,0); grid.addWidget(self.tax,2,1)
        grid.addWidget(add,2,2); grid.addWidget(delete,2,3)
        layout.addLayout(grid)

        self.sum_label = QLabel("Netto: 0.00 | Steuer: 0.00 | Brutto: 0.00")
        layout.addWidget(self.sum_label)
        btns = QHBoxLayout(); save = QPushButton("Speichern"); cancel = QPushButton("Abbrechen")
        btns.addStretch(1); btns.addWidget(save); btns.addWidget(cancel); layout.addLayout(btns)

        add.clicked.connect(self.add_item); delete.clicked.connect(self.remove_item); save.clicked.connect(self.accept); cancel.clicked.connect(self.reject)
        self._load_customers()

    def _load_customers(self):
        self.customers = self.customer_service.list_customers()
        self.customer_combo.clear(); self.customer_combo.addItem("Bitte wählen", None)
        for c in self.customers:
            self.customer_combo.addItem(f"{c.customer_number} - {c.name}", c.id)

    def add_item(self):
        try:
            item = self.invoice_service.calculate_item({"description": self.desc.text(), "quantity": float(self.qty.text()), "unit": self.unit.text(), "unit_price_net": float(self.price.text()), "tax_rate": float(self.tax.text())})
            self.items.append(item); self.refresh_items()
            self.desc.clear()
        except Exception as e:
            QMessageBox.warning(self, "Validierungsfehler", str(e))

    def remove_item(self):
        row = self.table.currentRow()
        if 0 <= row < len(self.items):
            self.items.pop(row); self.refresh_items()

    def refresh_items(self):
        self.table.setRowCount(len(self.items))
        totals = self.invoice_service.calculate_totals(self.items) if self.items else {"net_total":0,"tax_total":0,"gross_total":0}
        for r,i in enumerate(self.items):
            vals=[i['description'],i['quantity'],i.get('unit',''),i['unit_price_net'],i['tax_rate'],i['line_net'],i['line_tax'],i['line_gross']]
            for c,v in enumerate(vals): self.table.setItem(r,c,QTableWidgetItem(str(v)))
        self.sum_label.setText(f"Netto: {totals['net_total']:.2f} | Steuer: {totals['tax_total']:.2f} | Brutto: {totals['gross_total']:.2f}")

    def get_data(self):
        return {
            "customer_id": self.customer_combo.currentData(),
            "invoice_date": self.invoice_date.date().toPython(),
            "service_period": self.service_period.text().strip() or None,
            "due_date": self.due_date.date().toPython(),
            "status": self.status.text().strip() or "erstellt",
            "items": self.items,
        }
