import csv
import os

def rechnung_als_csv_speichern(produkte, dateiname="rechnung.csv"):
    os.makedirs(os.path.dirname(dateiname), exist_ok=True)

    with open(dateiname, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Produkt", "Preis", "Menge", "Gesamt", "Steuersatz (%)", "Steuerbetrag (€)"])

        for produkt, preis, menge, steuersatz in produkte:
            gesamt = preis * menge
            steuer_betrag = gesamt * (steuersatz / 100)
            writer.writerow([produkt, f"{preis:.2f}", menge, f"{gesamt:.2f}", steuersatz, f"{steuer_betrag:.2f}"])
