from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)


class CustomerDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, customer: object | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Kunde bearbeiten" if customer else "Neuer Kunde")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.customer_number_edit = QLineEdit()
        self.name_edit = QLineEdit()
        self.street_edit = QLineEdit()
        self.postal_code_edit = QLineEdit()
        self.city_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.phone_edit = QLineEdit()

        form.addRow("Kundennummer", self.customer_number_edit)
        form.addRow("Name", self.name_edit)
        form.addRow("Straße", self.street_edit)
        form.addRow("PLZ", self.postal_code_edit)
        form.addRow("Ort", self.city_edit)
        form.addRow("E-Mail", self.email_edit)
        form.addRow("Telefon", self.phone_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Speichern")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if customer:
            self.customer_number_edit.setText(customer.customer_number or "")
            self.name_edit.setText(customer.name or "")
            self.street_edit.setText(customer.street or "")
            self.postal_code_edit.setText(customer.postal_code or "")
            self.city_edit.setText(customer.city or "")
            self.email_edit.setText(customer.email or "")
            self.phone_edit.setText(customer.phone or "")

    def get_data(self) -> dict:
        return {
            "customer_number": self.customer_number_edit.text(),
            "name": self.name_edit.text(),
            "street": self.street_edit.text(),
            "postal_code": self.postal_code_edit.text(),
            "city": self.city_edit.text(),
            "email": self.email_edit.text(),
            "phone": self.phone_edit.text(),
        }
