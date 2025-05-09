# kunde.py Kunde-Klasse
# Diese Klasse repräsentiert einen Kunden mit Vorname, Nachname, Straße, PLZ und Ort.
# Sie enthält eine Methode zur Darstellung des Kunden als String.
#

class Kunde:
    def __init__(self, vorname, nachname, strasse, plz, ort):
        self.vorname = vorname
        self.nachname = nachname
        self.strasse = strasse
        self.plz = plz
        self.ort = ort

    def __str__(self):
        return f"{self.vorname} {self.nachname}, {self.strasse}, {self.plz} {self.ort}"
