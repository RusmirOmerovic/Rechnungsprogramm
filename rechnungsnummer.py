import os
from datetime import datetime

def lese_und_aktualisiere_rechnungsnummer():
    dateiname = "daten/rechnungsnummer.txt"
    os.makedirs("daten", exist_ok=True)

    monat_jahr = datetime.now().strftime("%y%m")

    if os.path.exists(dateiname):
        with open(dateiname, "r+", encoding="utf-8") as f:
            inhalt = f.read().strip()
            if inhalt.startswith(monat_jahr):
                aktuelle_nummer = int(inhalt.split("-")[1])
                neue_nummer = aktuelle_nummer + 1
            else:
                neue_nummer = 1
            neue_rechnungsnummer = f"{monat_jahr}-{neue_nummer:02d}"
            f.seek(0)
            f.write(neue_rechnungsnummer)
            f.truncate()
    else:
        neue_rechnungsnummer = f"{monat_jahr}-01"
        with open(dateiname, "w", encoding="utf-8") as f:
            f.write(neue_rechnungsnummer)

    return neue_rechnungsnummer
