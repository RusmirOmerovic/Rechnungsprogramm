from datetime import datetime
import os
from pdf_export import rechnung_als_pdf_speichern
from csv_export import rechnung_als_csv_speichern
from xml_export import rechnung_als_xml_speichern
from kundendaten import kundendaten_abfragen_wenn_noetig
from rechnungsnummer import lese_und_aktualisiere_rechnungsnummer

def produkte_eingeben():
    produkte = []
    while True:
        produkt = input("Geben Sie das Produkt ein ('exit' oder 'fertig' zum Beenden): ").strip()
        if produkt.lower() in ['fertig', 'exit']:
            print("✅ Eingabe beendet. Die Rechnung wird erstellt.")
            break
        elif any(p[0].lower() == produkt.lower() for p in produkte):
            print(f"⚠️ Das Produkt '{produkt}' wurde bereits eingegeben.")
            continue
        elif len(produkt) < 3 or not produkt.isalpha():
            print("❌ Der Produktname muss mindestens 3 Buchstaben enthalten und darf nur Buchstaben enthalten.")
            continue
        try:
            preis = float(input(f"💰 Preis pro Stück für '{produkt}': ").replace(",", "."))
            menge = int(input(f"🔢 Anzahl von '{produkt}': "))
            steuersatz = int(input("📊 MwSt-Satz (7 oder 19): "))
            while steuersatz not in [7, 19]:
                print("❌ Nur 7 oder 19 % erlaubt.")
                steuersatz = int(input("📊 MwSt-Satz (7 oder 19): "))
            produkte.append((produkt, preis, menge, steuersatz))
        except ValueError:
            print("❌ Bitte gültige Zahlen für Preis und Menge eingeben.")
    return produkte

def rechnung_speichern(produkte, dateiname):
    pfad = f"daten/{dateiname}"
    os.makedirs("daten", exist_ok=True)
    with open(pfad, "w", encoding="utf-8") as f:
        f.write("🧾 Rechnung:\n")
        f.write("-" * 65 + "\n")
        f.write("Produkt              Preis  Menge  Gesamt     MwSt\n")
        f.write("-" * 65 + "\n")
        for produkt, preis, menge, steuersatz in produkte:
            gesamt = preis * menge
            f.write(f"{produkt.ljust(20)} {preis:>5.2f} €   {menge:<5} {gesamt:>7.2f} €   {steuersatz}%\n")
    print(f"\n📁 Rechnung wurde erfolgreich in '{pfad}' gespeichert.")
    return pfad

# --- Hauptprogramm ---
if __name__ == "__main__":
    produkte = produkte_eingeben()
    kundendaten = kundendaten_abfragen_wenn_noetig()
    rechnungsnummer = lese_und_aktualisiere_rechnungsnummer()
    
    zeit = datetime.now().strftime("%Y-%m-%d_%H-%M")
    basisname = f"{rechnungsnummer}_{zeit}"

    pfad_txt = rechnung_speichern(produkte, f"{basisname}.txt")
    rechnung_als_csv_speichern(produkte, f"daten/{basisname}.csv")
    rechnung_als_pdf_speichern(produkte, kundendaten, f"daten/{basisname}.pdf")
    rechnung_als_xml_speichern(produkte, f"daten/{basisname}.xml")

    print(f"📊 CSV, 📄 PDF und 📄 XML wurden ebenfalls unter 'daten/' gespeichert.")
    print("✅ Rechnung erfolgreich erstellt!")