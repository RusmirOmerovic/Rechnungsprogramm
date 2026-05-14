from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class SimplePage(QWidget):
    def __init__(self, title: str, description: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        heading = QLabel(f"<h2>{title}</h2>")
        text = QLabel(description)
        text.setWordWrap(True)

        layout.addWidget(heading)
        layout.addWidget(text)
        layout.addStretch(1)
