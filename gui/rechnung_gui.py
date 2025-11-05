import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tkinter as tk
from tkinter import messagebox
import json
from models.kunde import Kunde
from models.position import Position
from models.rechnung import Rechnung
from rechnungsnummer import lese_und_aktualisiere_rechnungsnummer
from exports.pdf_export import PDFExporter
from exports.csv_export import rechnung_als_csv_speichern
from exports.xml_export import rechnung_als_xml_speichern

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
    geladene_daten = {}
    if os.path.exists(kunden_datei):
        try:
            with open(kunden_datei, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                rohdaten = json.loads(content)
                if isinstance(rohdaten, dict):
                    geladene_daten = rohdaten
                else:
                    messagebox.showwarning("Warnung", "kunden.json enthält unerwartete Daten. Die Kundenliste wurde zurückgesetzt.")
            else:
                geladene_daten = {}
        except (json.JSONDecodeError, OSError):
            messagebox.showwarning("Warnung", "kunden.json konnte nicht geladen werden. Die Kundenliste wurde zurückgesetzt.")
    kunden_liste = {}
    for name, daten in geladene_daten.items():
        if not isinstance(daten, dict):
            daten = {}
        vorname = daten.get("vorname", "").strip()
        nachname = daten.get("nachname", "").strip()
        if not (vorname or nachname):
            teile = name.split(" ", 1)
            vorname = teile[0] if teile else ""
            nachname = teile[1] if len(teile) > 1 else ""
        vollstaendiger_name = " ".join(filter(None, [vorname, nachname])).strip() or name
        kunden_liste[vollstaendiger_name] = {
            "vorname": vorname,
            "nachname": nachname,
            "strasse": daten.get("strasse", ""),
            "plz": daten.get("plz", ""),
            "ort": daten.get("ort", "")
        }

    aktuelle_auswahl = kunden_var.get()
    dropdown_kunden["menu"].delete(0, "end")
    for name in sorted(kunden_liste):
        dropdown_kunden["menu"].add_command(label=name, command=tk._setit(kunden_var, name, kunde_auswaehlen))

    if aktuelle_auswahl in kunden_liste:
        kunden_var.set(aktuelle_auswahl)
    else:
        kunden_var.set("Kundenliste")

# --- Kunde auswählen aus Dropdown ---
def kunde_auswaehlen(name):
    daten = kunden_liste.get(name, {})
    entry_vorname.delete(0, tk.END)
    entry_vorname.insert(0, daten.get("vorname", ""))
    entry_nachname.delete(0, tk.END)
    entry_nachname.insert(0, daten.get("nachname", ""))
    entry_strasse.delete(0, tk.END)
    entry_strasse.insert(0, daten.get("strasse", ""))
    entry_ort.delete(0, tk.END)
    plz = daten.get("plz", "")
    ort = daten.get("ort", "")
    entry_ort.insert(0, f"{plz} {ort}".strip())

# --- Kunde speichern ---
def speichere_kunde():
    vorname = entry_vorname.get().strip()
    nachname = entry_nachname.get().strip()
    if not vorname or not nachname:
        messagebox.showerror("Fehler", "Bitte Vor- und Nachnamen eingeben.")
        return

    strasse = entry_strasse.get().strip()
    plz_ort_text = entry_ort.get().strip()
    if not plz_ort_text:
        messagebox.showerror("Fehler", "PLZ und Ort korrekt eingeben.")
        return

    teile = plz_ort_text.split(None, 1)
    if len(teile) < 2:
        messagebox.showerror("Fehler", "PLZ und Ort korrekt eingeben.")
        return

    plz, ort = teile[0], teile[1].strip()
    voller_name = f"{vorname} {nachname}".strip()

    kunden_liste[voller_name] = {
        "vorname": vorname,
        "nachname": nachname,
        "strasse": strasse,
        "plz": plz,
        "ort": ort
    }

    with open(kunden_datei, "w", encoding="utf-8") as f:
        json.dump(kunden_liste, f, indent=2, ensure_ascii=False)

    lade_kunden()
    kunden_var.set(voller_name)
    kunde_auswaehlen(voller_name)
    messagebox.showinfo("Gespeichert", f"Kunde '{voller_name}' wurde gespeichert.")

# --- GUI-Eingabefelder: Kundendaten ---
tk.Label(root, text="Vorname:").pack()
entry_vorname = tk.Entry(root)
entry_vorname.pack()

tk.Label(root, text="Nachname:").pack()
entry_nachname = tk.Entry(root)
entry_nachname.pack()

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

def _baue_rechnung():
    vorname = entry_vorname.get().strip()
    nachname = entry_nachname.get().strip()
    if not vorname or not nachname:
        raise ValueError("Bitte Vor- und Nachnamen eingeben.")

    strasse = entry_strasse.get().strip()
    plz_ort_text = entry_ort.get().strip()

    teile = plz_ort_text.split(None, 1)
    if len(teile) < 2:
        raise ValueError("Bitte PLZ und Ort eingeben (z.B. 85560 München)")

    plz, ort = teile[0], teile[1].strip()

    kunde = Kunde(vorname, nachname, strasse, plz, ort)
    positionen = list(positionen_liste)
    if not positionen:
        raise ValueError("Bitte mindestens eine Position hinzufügen.")

    rechnungsnummer = lese_und_aktualisiere_rechnungsnummer()
    rechnung = Rechnung(rechnungsnummer, kunde, positionen)
    return rechnung


def exportiere_rechnung():
    try:
        rechnung = _baue_rechnung()

        exporter = PDFExporter(rechnung)
        pdf_path = exporter.export(f"rechnung_{rechnung.nummer}.pdf")
        csv_path = rechnung_als_csv_speichern(rechnung)
        xml_path = rechnung_als_xml_speichern(rechnung)

        messagebox.showinfo(
            "Erfolg",
            "Rechnung exportiert:\n"
            f"- PDF: {pdf_path}\n"
            f"- CSV: {csv_path}\n"
            f"- XML: {xml_path}",
        )
    except Exception as e:
        messagebox.showerror("Fehler", str(e))

# --- Buttons für Positionen + PDF ---
tk.Button(root, text="➕ Position hinzufügen", command=add_position).pack(pady=3)
tk.Button(root, text="❌ Position löschen", command=loesche_position).pack(pady=3)
tk.Button(root, text="📄 Exporte erzeugen", command=exportiere_rechnung).pack(pady=10)

# --- Programm starten ---
lade_kunden()
root.mainloop()
# --- Ende der GUI ---
