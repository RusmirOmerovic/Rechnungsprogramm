import os

def kundendaten_abfragen_wenn_noetig():
    dateiname = "daten/kundendaten.txt"
    os.makedirs("daten", exist_ok=True)

    if os.path.exists(dateiname):
        with open(dateiname, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print("📄 Bitte gib die Firmendaten ein (werden gespeichert):")
        name = input("Name der Firma: ")
        adresse = input("Adresse: ")
        telefon = input("Telefon: ")
        email = input("E-Mail: ")

        daten = f"{name}\n{adresse}\nTelefon: {telefon}\nE-Mail: {email}"

        with open(dateiname, "w", encoding="utf-8") as f:
            f.write(daten)
        return daten
