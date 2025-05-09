# rechnung.py

from kunde import Kunde
from position import Position
import datetime

class Rechnung:
    def __init__(self, nummer, kunde: Kunde, positionen: list[Position], datum=None):
        self.nummer = nummer
        self.kunde = kunde
        self.positionen = positionen
        self.datum = datum or datetime.date.today()

    @property
    def gesamtbetrag(self):
        return sum(p.gesamtpreis for p in self.positionen)

    def __str__(self):
        pos_str = "\n".join(str(p) for p in self.positionen)
        return (
            f"Rechnung Nr. {self.nummer}\n"
            f"Kunde: {self.kunde}\n"
            f"Datum: {self.datum.strftime('%d.%m.%Y')}\n"
            f"Positionen:\n{pos_str}\n"
            f"Gesamtbetrag: {self.gesamtbetrag:.2f}€"
        )
