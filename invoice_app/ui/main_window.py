from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from invoice_app.pages.simple_page import SimplePage


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

        for title, description in sections:
            self.navigation.addItem(QListWidgetItem(title))
            self.pages.addWidget(SimplePage(title, description))

        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.navigation.setCurrentRow(0)

        layout.addWidget(self.navigation)
        layout.addWidget(self.pages, 1)
        self.setCentralWidget(container)
        self.statusBar().showMessage("Bereit", 3000)
        self.navigation.setFocusPolicy(Qt.FocusPolicy.NoFocus)
