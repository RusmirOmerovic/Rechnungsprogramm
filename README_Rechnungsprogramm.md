# 🧮 Rechnungsprogramm – Python (GUI, PDF, XML/CSV)

**Autor:** Rusmir Omerovic  
**Stand:** 2025-10-29  
**Ziel:** Rechnungen schnell & einfach erstellen, als **PDF** sauber ausgeben, optional **XML/CSV** exportieren – per **GUI** und (später) CLI.

---

## ✨ Features (v1.0 Zielbild)
- **GUI (tkinter):** Kunden und Positionen anlegen, bearbeiten, löschen
- **Rechnungsnummer-Automatik:** fortlaufend (z. B. `YYMM-XX`)
- **PDF-Export (fpdf2):** Logo, Absender/Empfänger, Tabelle, Netto/UST/Brutto, Datum, **Leistungszeitraum**
- **XML/CSV-Export:** strukturierte Daten zur Weiterverarbeitung
- **Saubere Ordnerstruktur & Logs**
- **Einheitliches Dateinamensschema:** `Rechnung_<Nr>_<KundeKurz>_<YYYYMMDD>.pdf`

> Hinweis: Einige Punkte sind in Arbeit (siehe Roadmap). Diese README beschreibt das Zielbild und die Verwendung.
 
---

## 🚀 Quickstart (macOS / Linux)

```bash
# 1) Repository klonen
git clone <DEIN-REPO> rechnungsprogramm
cd rechnungsprogramm

# 2) Virtuelle Umgebung + Abhängigkeiten
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3) Schnelltest ohne GUI
python -m tests.test_rechnung   # erzeugt ein Test-PDF unter tests/

# 4) GUI starten
python gui/rechnung_gui.py
```

**Erwartung:** Es werden PDFs (und optional XML/CSV) erzeugt. Standard-Ausgabepfad (Roadmap): `exports/out/`.

---

## 🖥️ Verwendung (GUI)

1. **Programm starten**: `python gui/rechnung_gui.py`  
2. **Kunde wählen / anlegen** (Name, Adresse, USt-ID optional)  
3. **Positionen hinzufügen** (Beschreibung, Menge, Preis)  
4. **Leistungszeitraum** eintragen (z. B. „01.10–31.10.2025“)  
5. **Rechnung erzeugen** → PDF wird gespeichert

**Live-Summe:** wird nach jeder Änderung aktualisiert (Roadmap).

---

## ✅ Manuelle Prüfliste Kundenvalidierung

- Kunde anlegen (gültige Daten)
- Kunde mit leerem Namen
- Kunde mit leerer Kundennummer
- Kunde mit ungültiger E-Mail (ohne `@`)
- Kunde mit ungültiger PLZ (nicht-numerisch)
- Kunde bearbeiten
- Kunde löschen

---

## 🧪 Tests

Ein einfacher Regressions-Test erzeugt ein Test-PDF:
```bash
python -m tests.test_rechnung
```
Geplante Unit-Tests (Roadmap):
- `test_invoice_number.py` – fortlaufende Rechnungsnummer
- `test_xml_valid.py` – XML parst ohne Fehler
- `test_pdf_created.py` – PDF-Datei existiert & > 0 KB

---

## 📁 Projektstruktur (Zielstruktur)

```
.
├─ daten/                 # Stammdaten/Beispiele (Kunden, Produkte)
├─ exports/
│  ├─ out/                # Exportierte Rechnungen (PDF, XML, CSV)
│  ├─ pdf_export.py       # PDF-Exporter (fpdf2)
│  ├─ xml_export.py       # XML-Export
│  └─ csv_export.py       # CSV-Export
├─ fonts/                 # Schriftarten (z. B. DejaVu)
├─ gui/
│  ├─ rechnung_gui.py     # GUI (tkinter) – Startpunkt
│  └─ main_gui.py         # (optional) Wrapper/Launcher
├─ logs/                  # app.log
├─ models/
│  ├─ rechnung.py         # Rechnung, Kunde, Position (+ Validierung)
│  └─ ...
├─ utils/
│  ├─ filename.py         # Dateinamen-Helfer
│  └─ ...
├─ tests/
│  ├─ test_rechnung.py    # Smoke-Test PDF
│  └─ ...
├─ rechnungsnummer.py     # Zähler/Generator für Rechnungsnummern
├─ requirements.txt
└─ README.md
```

---

## ⚙️ Konfiguration

- **Logo/Schriften:** in `fonts/` ablegen und im PDF-Exporter referenzieren.
- **USt-Satz:** zentral definieren (z. B. 19 %), später parametrisierbar.
- **Ausgabepfad:** standardmäßig `exports/out/` (wird beim Export erstellt).
- **Dateinamen:** werden über `utils/filename.py` konsistent erzeugt.

---

## 🧰 CLI (optional)

Für Automatisierung/Tests kann ein Sample-Export erfolgen:
```bash
python -m utils.generate_invoice --sample
```
Erzeugt eine Beispielrechnung mit Dummy-Daten in `exports/out/`.

---

## 🧩 Troubleshooting

- **GUI startet nicht (macOS):** Python von python.org nutzen; sicherstellen, dass Tcl/Tk vollständig vorhanden ist.
- **`ModuleNotFoundError`:** Prüfen, ob `.venv` aktiv ist, dann `pip install -r requirements.txt` erneut.
- **Keine Dateien erzeugt:** Sicherstellen, dass der Exportpfad existiert bzw. `os.makedirs("exports/out", exist_ok=True)` gesetzt ist.
- **Falsches Encoding/Dezimaltrennzeichen:** CSV-Export anpassen (UTF‑8, Komma/ Punkt konsistent).

---

## 🗺️ Roadmap (nächste Schritte zu v1.0)

1. **Einheitlicher Exportpfad** `exports/out/` für GUI, Tests & CLI  
2. **Rechnungsnummer-Automatik** (Nutzung in GUI & Tests)  
3. **Leistungszeitraum** im Modell + PDF-Header + GUI-Feld  
4. **Live-Summenanzeige** in der GUI  
5. **XML/CSV an Rechnung koppeln** (Adapter aus `rechnung.positionen`)  
6. **Dateinamensschema** (safe Kundenkürzel + Datum)  
7. **Unit-Tests** (Nummer, XML-Parse, PDF-Größe)  
8. **Release `v1.0.0`**: README + Screens (`docs/gui.png`, `docs/pdf.png`, `docs/terminal.png`)

---

## 🏷️ Lizenz

MIT (sofern nicht anders angegeben). Bitte Lizenz anpassen, falls erforderlich.

---

## 🤝 Beiträge

Issues/PRs willkommen – Fokus auf klare, kleine Verbesserungen (Tests, PDFs, GUI-UX).
