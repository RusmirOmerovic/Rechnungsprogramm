import sys
from PySide6.QtWidgets import QApplication

from invoice_app.database.init_db import init_database
from invoice_app.ui.main_window import MainWindow


def run() -> int:
    init_database()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
