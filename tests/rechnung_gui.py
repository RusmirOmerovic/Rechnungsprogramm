import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))



import tkinter as tk
from tkinter import messagebox
import json
import os
from models.kunde import Kunde
from models.position import Position
from models.rechnung import Rechnung
from exports.pdf_export import PDFExporter

# Fenster starten
root = tk.Tk()
root.title("Rechnungsprogramm")

# --- Positionenliste und Kundenverwaltung ---
positionen_liste = []
kunden_liste = {}  # Dict für gespeicherte Kunden
kunden_datei = "daten/kunden.json"

# Stelle sicher, dass daten/-Ordner existiert
os.makedirs("daten", exist_ok=True)

# --- Kundenverwaltung laden ---
def lade_kunden():
    global kunden_liste
    if os.path.exists(kunden_datei):
        try:
            with open(kunden_datei, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    kunden_liste = json.loads(content)
                else:
                    kunden_liste = {}
        except json.JSONDecodeError:
            kunden_liste = {}
            messagebox.showwarning("Warnung", "kunden.json ist beschädigt. Es wurden keine Kunden geladen.")
    else:
        kunden_liste = {}

    # Dropdown aktualisieren
    dropdown_kunden["menu"].delete(0, "end")
    for name in kunden_liste:
        dropdown_kunden["menu"].add_command(label=name, command=tk._setit(kunden_var, name, kunde_auswaehlen))


# --- Kunde auswählen aus Dropdown ---
def kunde_auswaehlen(name):
    daten = kunden_liste.get(name)
    if daten:
        entry_name.delete(0, tk.END)
        entry_name.insert(0, name)
        entry_strasse.delete(0, tk.END)
        entry_strasse.insert(0, daten["strasse"])
        entry_ort.delete(0, tk.END)
        entry_ort.insert(0, f'{daten["plz"]} {daten["ort"]}')

# --- Kunde speichern ---
def speichere_kunde():
    name = entry_name.get()
    strasse = entry_strasse.get()
    plz_ort = entry_ort.get().split(" ")
    if len(plz_ort) < 2:
        messagebox.showerror("Fehler", "PLZ und Ort korrekt eingeben.")
        return

    kunden_liste[name] = {
        "strasse": strasse,
        "plz": plz_ort[0],
        "ort": " ".join(plz_ort[1:])
    }

    with open(kunden_datei, "w", encoding="utf-8") as f:
        json.dump(kunden_liste, f, indent=2, ensure_ascii=False)

    lade_kunden()
    messagebox.showinfo("Gespeichert", f"Kunde '{name}' wurde gespeichert.")

# --- GUI-Eingabefelder: Kundendaten ---
tk.Label(root, text="Kunde:").pack()
entry_name = tk.Entry(root)
entry_name.pack()

tk.Label(root, text="Straße:").pack()
entry_strasse = tk.Entry(root)
entry_strasse.pack()

tk.Label(root, text="PLZ Ort:").pack()
entry_ort = tk.Entry(root)
entry_ort.pack()

# --- Kundenauswahl-Dropdown ---
tk.Label(root, text="Gespeicherte Kunden auswählen:").pack()
kunden_var = tk.StringVar(root)
kunden_var.set("Kundenliste")
dropdown_kunden = tk.OptionMenu(root, kunden_var, ())
dropdown_kunden.pack()

# --- Buttons für Kunden ---
tk.Button(root, text="💾 Kunde speichern", command=speichere_kunde).pack(pady=3)

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

# --- Listbox für Positionen ---
tk.Label(root, text="Positionen:").pack()
positions_listbox = tk.Listbox(root, width=60, height=8)
positions_listbox.pack()

# --- Gesamtsumme anzeigen ---
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

# --- Buttons für Positionen + PDF ---
tk.Button(root, text="➕ Position hinzufügen", command=add_position).pack(pady=3)
tk.Button(root, text="❌ Position löschen", command=loesche_position).pack(pady=3)
tk.Button(root, text="📄 PDF erzeugen", command=erstelle_pdf).pack(pady=10)

# --- Programm starten ---
lade_kunden()
root.mainloop()
# --- Ende der GUI ---