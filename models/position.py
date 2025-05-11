# position.py # Position-Klasse
# Diese Klasse repräsentiert eine Position in einer Rechnung mit Beschreibung, Menge und Einzelpreis.
# Sie enthält eine Methode zur Berechnung des Gesamtpreises und eine Methode zur Darstellung der Position als String.
# #

from utils.logger import log_error
from models.errors import InvalidPositionError

class Position:
    def __init__(self, beschreibung, menge, einzelpreis):
        if not beschreibung or not isinstance(beschreibung, str):
            log_error(f"Ungültige Beschreibung: {beschreibung}")
            raise InvalidPositionError("Beschreibung muss ein nicht-leerer Text sein.")
        if not isinstance(menge, int) or menge <= 0:
            log_error(f"Ungültige Menge: {menge}")
            raise InvalidPositionError("Menge muss eine positive ganze Zahl sein.")
        if not isinstance(einzelpreis, (int, float)) or einzelpreis < 0:
            log_error(f"Ungültiger Einzelpreis: {einzelpreis}")
            raise InvalidPositionError("Einzelpreis muss eine positive Zahl sein.")

        self.beschreibung = beschreibung
        self.menge = menge
        self.einzelpreis = einzelpreis


    @property
    def gesamtpreis(self):
        return self.menge * self.einzelpreis

    def __str__(self):
        return f"{self.beschreibung}: {self.menge} x {self.einzelpreis:.2f}€ = {self.gesamtpreis:.2f}€"
