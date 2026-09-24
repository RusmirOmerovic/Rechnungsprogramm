from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QFormLayout, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget
)

from invoice_app.services.customer_service import CustomerService
from invoice_app.services.invoice_service import InvoiceService, InvoiceValidationError


class InvoiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neue Rechnung")
        self.resize(900, 650)
        self.customer_service = CustomerService()
        self.invoice_service = InvoiceService()
        self.items = []
        self._saving = False
        self._saved = False

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.customer_combo = QComboBox()
        self.customer_combo.setMinimumContentsLength(28)
        self.customer_combo.setMinimumWidth(320)
        self.customer_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.customer_combo.setAccessibleName("Kunde (Pflichtfeld)")
        self.customer_field = QFrame()
        customer_layout = QVBoxLayout(self.customer_field)
        customer_layout.setContentsMargins(4, 4, 4, 4)
        customer_layout.addWidget(self.customer_combo)
        self.customer_error = QLabel()
        self.customer_error.setTextFormat(Qt.TextFormat.PlainText)
        self.customer_error.setWordWrap(True)
        self.customer_error.hide()
        customer_layout.addWidget(self.customer_error)
        self.customer_combo.currentIndexChanged.connect(self._clear_customer_error)
        self.invoice_date = QDateEdit(QDate.currentDate()); self.invoice_date.setCalendarPopup(True)
        self.service_period_mode = QComboBox()
        for title, mode in [("Keine Angabe", "none"), ("Einzelnes Datum", "single"), ("Zeitraum", "range")]:
            self.service_period_mode.addItem(title, mode)
        self.service_date_from = QDateEdit(QDate.currentDate())
        self.service_date_to = QDateEdit(QDate.currentDate())
        self.service_dates = QWidget()
        service_dates_layout = QFormLayout(self.service_dates)
        service_dates_layout.setContentsMargins(0, 0, 0, 0)
        self.service_from_label = QLabel("Datum")
        self.service_to_label = QLabel("Bis")
        service_dates_layout.addRow(self.service_from_label, self.service_date_from)
        service_dates_layout.addRow(self.service_to_label, self.service_date_to)
        self.service_period_mode.currentIndexChanged.connect(self._update_service_dates)
        self._update_service_dates()
        self.due_date = QDateEdit(QDate.currentDate()); self.due_date.setCalendarPopup(True)
        for editor in (self.invoice_date, self.due_date, self.service_date_from, self.service_date_to):
            editor.setCalendarPopup(True)
            editor.setDisplayFormat("dd.MM.yyyy")
        self.status = QLineEdit("erstellt")
        form.addRow("Kunde (Pflichtfeld)", self.customer_field)
        form.addRow("Rechnungsdatum", self.invoice_date)
        form.addRow("Leistungsangabe", self.service_period_mode)
        form.addRow(self.service_dates)
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
        self.save_error = QLabel()
        self.save_error.setTextFormat(Qt.TextFormat.PlainText)
        self.save_error.setWordWrap(True)
        self.save_error.hide()
        layout.addWidget(self.save_error)
        btns = QHBoxLayout()
        self.save_button = QPushButton("Speichern")
        self.cancel_button = QPushButton("Abbrechen")
        for button in (add, delete, self.cancel_button):
            button.setAutoDefault(False)
        self.save_button.setDefault(True)
        btns.addStretch(1); btns.addWidget(self.save_button); btns.addWidget(self.cancel_button); layout.addLayout(btns)

        add.clicked.connect(self.add_item); delete.clicked.connect(self.remove_item)
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        tab_order = [self.customer_combo, self.invoice_date, self.service_period_mode,
                     self.service_date_from, self.service_date_to, self.due_date,
                     self.status, self.table, self.desc, self.qty, self.unit,
                     self.price, self.tax, add, delete, self.save_button, self.cancel_button]
        for previous, following in zip(tab_order, tab_order[1:]):
            self.setTabOrder(previous, following)
        self._load_customers()

    def _load_customers(self):
        self.customers = self.customer_service.list_customers()
        self.customer_combo.clear(); self.customer_combo.addItem("Bitte Kunden auswählen", None)
        for c in self.customers:
            self.customer_combo.addItem(f"{c.customer_number} - {c.name}", c.id)
        self.customer_combo.setCurrentIndex(0)

    def _clear_customer_error(self):
        if self.customer_combo.currentData() is not None:
            self.customer_error.clear()
            self.customer_error.hide()
            self.customer_field.setFrameShape(QFrame.Shape.NoFrame)
            self.customer_combo.setAccessibleDescription("")

    def _update_service_dates(self):
        mode = self.service_period_mode.currentData()
        self.service_dates.setVisible(mode != "none")
        self.service_date_from.setEnabled(mode != "none")
        self.service_from_label.setText("Von" if mode == "range" else "Datum")
        self.service_date_to.setVisible(mode == "range")
        self.service_date_to.setEnabled(mode == "range")
        self.service_to_label.setVisible(mode == "range")

    def accept(self):
        """The sole save path, shared by the default button and Enter."""
        if self._saving or self._saved:
            return
        self._saving = True
        self.save_button.setEnabled(False)
        self.save_error.clear()
        self.save_error.hide()
        try:
            self.invoice_service.create_invoice(self.get_data())
        except InvoiceValidationError as error:
            if error.field == "customer_id":
                self.customer_error.setText(str(error))
                self.customer_error.show()
                # Keep the native combo/dropdown appearance in light/dark themes.
                self.customer_field.setFrameShape(QFrame.Shape.Box)
                self.customer_combo.setAccessibleDescription(str(error))
                self.customer_combo.setFocus()
            else:
                self.save_error.setText(str(error))
                self.save_error.show()
                fields = {"invoice_date": self.invoice_date, "due_date": self.due_date,
                          "items": self.desc, "service_period_mode": self.service_period_mode,
                          "service_date_from": self.service_date_from, "service_date_to": self.service_date_to}
                field = fields.get(error.field)
                if field is not None:
                    field.setFocus()
        except ValueError as error:
            self.save_error.setText(str(error))
            self.save_error.show()
        except Exception as error:
            self.save_error.setText(f"Rechnung konnte nicht gespeichert werden. Ihre Eingaben bleiben erhalten.\nDetails: {error}")
            self.save_error.show()
        else:
            self._saved = True
            super().accept()
        finally:
            self._saving = False
            self.save_button.setEnabled(not self._saved)

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
        mode = self.service_period_mode.currentData()
        return {
            "customer_id": self.customer_combo.currentData(),
            "invoice_date": self.invoice_date.date().toPython(),
            "service_period_mode": mode,
            "service_date_from": self.service_date_from.date().toPython() if mode in ("single", "range") else None,
            "service_date_to": self.service_date_to.date().toPython() if mode == "range" else None,
            "due_date": self.due_date.date().toPython(),
            "status": self.status.text().strip() or "erstellt",
            "items": self.items,
        }
