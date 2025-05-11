import tkinter as tk
from tkinter import messagebox
from models.kunde import Kunde
from models.position import Position
from models.rechnung import Rechnung
from exports.pdf_export import PDFExporter
import os

# Fenster starten
root = tk.Tk()
root.title("Rechnungsprogramm")

# Liste für Positionen
positionen_liste = []

# --- Eingabefelder Kunde ---
tk.Label(root, text="Kunde:").pack()
entry_name = tk.Entry(root)
entry_name.pack()

tk.Label(root, text="Straße:").pack()
entry_strasse = tk.Entry(root)
entry_strasse.pack()

tk.Label(root, text="PLZ Ort:").pack()
entry_ort = tk.Entry(root)
entry_ort.pack()

# --- Eingabefelder Position ---
tk.Label(root, text="Leistung:").pack()
entry_beschreibung = tk.Entry(root)
entry_beschreibung.pack()

tk.Label(root, text="Menge:").pack()
entry_menge = tk.Entry(root)
entry_menge.pack()

tk.Label(root, text="Einzelpreis:").pack()
entry_preis = tk.Entry(root)
entry_preis.pack()

# --- Listbox für Positionen + Gesamtsumme ---
tk.Label(root, text="Positionen:").pack()
positions_listbox = tk.Listbox(root, width=60, height=8)
positions_listbox.pack()

gesamt_label = tk.Label(root, text="Gesamtsumme: 0.00€")
gesamt_label.pack()

# --- Funktionen ---
def aktualisiere_positionen_liste():
    positions_listbox.delete(0, tk.END)
    summe = 0
    for idx, p in enumerate(positionen_liste):
        text = f"{idx+1}. {p.beschreibung} – {p.menge} x {p.einzelpreis:.2f}€ = {p.gesamtpreis:.2f}€"
        positions_listbox.insert(tk.END, text)
        summe += p.gesamtpreis
    gesamt_label.config(text=f"Gesamtsumme: {summe:.2f}€")

def add_position():
    try:
        beschreibung = entry_beschreibung.get()
        menge = int(entry_menge.get())
        preis = float(entry_preis.get())

        position = Position(beschreibung, menge, preis)
        positionen_liste.append(position)

        aktualisiere_positionen_liste()

        entry_beschreibung.delete(0, tk.END)
        entry_menge.delete(0, tk.END)
        entry_preis.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Fehler", str(e))

def loesche_position():
    auswahl = positions_listbox.curselection()
    if not auswahl:
        return
    index = auswahl[0]
    del positionen_liste[index]
    aktualisiere_positionen_liste()

def erstelle_pdf():
    try:
        name = entry_name.get()
        strasse = entry_strasse.get()
        plz_ort = entry_ort.get().split(" ")

        if len(plz_ort) < 2:
            raise ValueError("Bitte PLZ und Ort eingeben (z.B. 85560 München)")

        kunde = Kunde(name, "", strasse, plz_ort[0], " ".join(plz_ort[1:]))
        rechnung = Rechnung("2025-001", kunde, positionen_liste)

        os.makedirs("tests", exist_ok=True)
        exporter = PDFExporter(rechnung)
        exporter.export("tests/rechnung_gui.pdf")

        messagebox.showinfo("Erfolg", "PDF wurde erstellt: tests/rechnung_gui.pdf")
    except Exception as e:
        messagebox.showerror("Fehler", str(e))

# --- Buttons ---
tk.Button(root, text="➕ Position hinzufügen", command=add_position).pack(pady=3)
tk.Button(root, text="❌ Position löschen", command=loesche_position).pack(pady=3)
tk.Button(root, text="📄 PDF erzeugen", command=erstelle_pdf).pack(pady=10)

root.mainloop()
