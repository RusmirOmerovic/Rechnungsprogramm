# position.py # Position-Klasse
# Diese Klasse repräsentiert eine Position in einer Rechnung mit Beschreibung, Menge und Einzelpreis.
# Sie enthält eine Methode zur Berechnung des Gesamtpreises und eine Methode zur Darstellung der Position als String.
# #

from models.errors import InvalidPositionError

class Position:
    def __init__(self, beschreibung, menge, einzelpreis):
        
        if not beschreibung or not isinstance(beschreibung, str):
            raise ValueError("Beschreibung muss ein nicht-leerer Text sein.")
        if not isinstance(menge, int) or menge <= 0:
            raise ValueError("Menge muss eine positive ganze Zahl sein.")
        if not isinstance(einzelpreis, (int, float)) or einzelpreis < 0:
            raise InvalidPositionError("Einzelpreis muss eine positive Zahl sein.")

        self.beschreibung = beschreibung
        self.menge = menge
        self.einzelpreis = einzelpreis

    @property
    def gesamtpreis(self):
        return self.menge * self.einzelpreis

    def __str__(self):
        return f"{self.beschreibung}: {self.menge} x {self.einzelpreis:.2f}€ = {self.gesamtpreis:.2f}€"
