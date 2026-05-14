from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from invoice_app.dialogs.customer_dialog import CustomerDialog
from invoice_app.services.customer_service import CustomerService


class CustomersPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.service = CustomerService()
        self.customers = []

        root_layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Kundennummer", "Name", "Straße", "PLZ", "Ort", "E-Mail", "Telefon"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.show_selected_details)

        root_layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.new_button = QPushButton("Neu")
        self.edit_button = QPushButton("Bearbeiten")
        self.delete_button = QPushButton("Löschen")
        self.refresh_button = QPushButton("Aktualisieren")
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.refresh_button)
        root_layout.addLayout(button_layout)

        detail_box = QWidget()
        self.detail_form = QFormLayout(detail_box)
        self.detail_labels: dict[str, QLabel] = {}
        for key, text in [
            ("id", "ID"),
            ("customer_number", "Kundennummer"),
            ("name", "Name"),
            ("street", "Straße"),
            ("postal_code", "PLZ"),
            ("city", "Ort"),
            ("email", "E-Mail"),
            ("phone", "Telefon"),
        ]:
            label = QLabel("-")
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self.detail_form.addRow(f"{text}:", label)
            self.detail_labels[key] = label
        root_layout.addWidget(detail_box)

        self.new_button.clicked.connect(self.create_customer)
        self.edit_button.clicked.connect(self.edit_customer)
        self.delete_button.clicked.connect(self.delete_customer)
        self.refresh_button.clicked.connect(self.load_customers)

        self.load_customers()

    def load_customers(self) -> None:
        try:
            self.customers = self.service.list_customers()
        except Exception as error:
            QMessageBox.critical(self, "Fehler", f"Kunden konnten nicht geladen werden:\n{error}")
            return

        self.table.setRowCount(len(self.customers))
        for row, customer in enumerate(self.customers):
            values = [
                customer.id,
                customer.customer_number,
                customer.name,
                customer.street or "",
                customer.postal_code or "",
                customer.city or "",
                customer.email or "",
                customer.phone or "",
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(str(value)))

        if self.customers:
            self.table.selectRow(0)
            self.show_customer_details(self.customers[0])
        else:
            self.clear_details()

    def get_selected_customer_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.customers):
            return None
        return self.customers[row].id

    def show_selected_details(self) -> None:
        customer_id = self.get_selected_customer_id()
        if customer_id is None:
            self.clear_details()
            return
        customer = next((c for c in self.customers if c.id == customer_id), None)
        if customer:
            self.show_customer_details(customer)

    def show_customer_details(self, customer) -> None:
        self.detail_labels["id"].setText(str(customer.id))
        self.detail_labels["customer_number"].setText(customer.customer_number or "-")
        self.detail_labels["name"].setText(customer.name or "-")
        self.detail_labels["street"].setText(customer.street or "-")
        self.detail_labels["postal_code"].setText(customer.postal_code or "-")
        self.detail_labels["city"].setText(customer.city or "-")
        self.detail_labels["email"].setText(customer.email or "-")
        self.detail_labels["phone"].setText(customer.phone or "-")

    def clear_details(self) -> None:
        for label in self.detail_labels.values():
            label.setText("-")

    def create_customer(self) -> None:
        dialog = CustomerDialog(self)
        if dialog.exec():
            try:
                self.service.create_customer(dialog.get_data())
                self.load_customers()
            except Exception as error:
                QMessageBox.critical(self, "Fehler", str(error))

    def edit_customer(self) -> None:
        customer_id = self.get_selected_customer_id()
        if customer_id is None:
            QMessageBox.information(self, "Hinweis", "Bitte zuerst einen Kunden auswählen.")
            return
        customer = next((c for c in self.customers if c.id == customer_id), None)
        if customer is None:
            return
        dialog = CustomerDialog(self, customer)
        if dialog.exec():
            try:
                self.service.update_customer(customer_id, dialog.get_data())
                self.load_customers()
            except Exception as error:
                QMessageBox.critical(self, "Fehler", str(error))

    def delete_customer(self) -> None:
        customer_id = self.get_selected_customer_id()
        if customer_id is None:
            QMessageBox.information(self, "Hinweis", "Bitte zuerst einen Kunden auswählen.")
            return

        confirm = QMessageBox.question(
            self,
            "Kunde löschen",
            "Möchten Sie den ausgewählten Kunden wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            self.service.delete_customer(customer_id)
            self.load_customers()
        except Exception as error:
            QMessageBox.critical(self, "Fehler", str(error))
