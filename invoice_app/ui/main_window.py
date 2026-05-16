from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from invoice_app.pages.customers_page import CustomersPage
from invoice_app.pages.simple_page import SimplePage
from invoice_app.pages.invoices_page import InvoicesPage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Invoice App")
        self.resize(1100, 700)

        container = QWidget(self)
        layout = QHBoxLayout(container)

        self.navigation = QListWidget()
        self.navigation.setFixedWidth(220)
        self.navigation.setSpacing(4)

        self.pages = QStackedWidget()

        sections = [
            ("Überblick", "Dashboard mit wichtigsten Kennzahlen und Schnellaktionen."),
            ("Kunden", "Verwaltung von Kundenstammdaten und Kontakten."),
            ("Rechnungen", "Erstellung und Bearbeitung von Rechnungen."),
            ("Archiv", "Historie abgeschlossener und exportierter Rechnungen."),
            ("Einstellungen", "App-Einstellungen, Nummernkreise und Standardwerte."),
        ]

        for index, (title, description) in enumerate(sections):
            self.navigation.addItem(QListWidgetItem(title))
            if index == 1:
                self.pages.addWidget(CustomersPage())
            elif index == 2:
                self.pages.addWidget(InvoicesPage())
            else:
                self.pages.addWidget(SimplePage(title, description))

        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.navigation.setCurrentRow(0)

        layout.addWidget(self.navigation)
        layout.addWidget(self.pages, 1)
        self.setCentralWidget(container)
        self.statusBar().showMessage("Bereit", 3000)
        self.navigation.setFocusPolicy(Qt.FocusPolicy.NoFocus)
