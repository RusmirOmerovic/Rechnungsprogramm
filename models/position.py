# position.py # Position-Klasse
# Diese Klasse repräsentiert eine Position in einer Rechnung mit Beschreibung, Menge und Einzelpreis.
# Sie enthält eine Methode zur Berechnung des Gesamtpreises und eine Methode zur Darstellung der Position als String.
# #

class Position:
    def __init__(self, beschreibung, menge, einzelpreis):
        self.beschreibung = beschreibung
        self.menge = menge
        self.einzelpreis = einzelpreis

    @property
    def gesamtpreis(self):
        return self.menge * self.einzelpreis

    def __str__(self):
        return f"{self.beschreibung}: {self.menge} x {self.einzelpreis:.2f}€ = {self.gesamtpreis:.2f}€"
