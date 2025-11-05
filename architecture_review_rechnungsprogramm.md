# Architektur-Review – Rechnungsprogramm

**Projektwurzel:** `/mnt/data/rechnungsprogramm/Rechnungsprogramm-main`

## 1. Struktur-Snapshot (Top 3 Ebenen)

```
Rechnungsprogramm-main
├── daten
│   ├── kunden.json
│   └── rechnungsnummer.txt
├── exports
│   ├── __init__.py
│   ├── csv_export.py
│   ├── export_utils.py
│   ├── pdf_export.py
│   └── xml_export.py
├── fonts
│   ├── DejaVuSans-Bold.ttf
│   ├── DejaVuSans.cw127.pkl
│   ├── DejaVuSans.pkl
│   └── DejaVuSans.ttf
├── gui
│   ├── __init__.py
│   ├── einstellungen_gui.py
│   ├── kunden_gui.py
│   ├── main_gui.py
│   ├── rechnung_gui.py
│   └── statistik_gui.py
├── logs
│   └── app.log
├── models
│   ├── errors.py
│   ├── kunde.py
│   ├── position.py
│   └── rechnung.py
├── tests
│   ├── rechnung_gui.py
│   └── test_rechnung.py
├── utils
│   └── logger.py
├── .DS_Store
├── .gitignore
├── icon.png
├── README_Rechnungsprogramm.md
├── rechnungsnummer.py
├── requirements.txt
├── setup.sh
└── start.sh
```
## 2. Abhängigkeiten & Frameworks

### 2.1 Erkannte Imports (Top-Dateien)

- `gui/rechnung_gui.py` – LOC: 263, Klassen: 0, Funktionen: 8
  - Imports: exports, json, models, os, rechnungsnummer, sys, tkinter
- `tests/rechnung_gui.py` – LOC: 190, Klassen: 0, Funktionen: 7
  - Imports: exports, json, models, os, sys, tkinter
- `exports/pdf_export.py` – LOC: 88, Klassen: 1, Funktionen: 7
  - Imports: , fpdf, models, pathlib
- `tests/test_rechnung.py` – LOC: 48, Klassen: 0, Funktionen: 0
  - Imports: exports, models, rechnungsnummer
- `exports/xml_export.py` – LOC: 47, Klassen: 0, Funktionen: 1
  - Imports: , models, pathlib, xml
- `exports/export_utils.py` – LOC: 41, Klassen: 1, Funktionen: 4
  - Imports: dataclasses, models, typing
- `exports/csv_export.py` – LOC: 40, Klassen: 0, Funktionen: 1
  - Imports: , csv, models, pathlib
- `gui/main_gui.py` – LOC: 38, Klassen: 0, Funktionen: 1
  - Imports: os, subprocess, sys, tkinter
- `models/position.py` – LOC: 31, Klassen: 1, Funktionen: 3
  - Imports: models, utils
- `rechnungsnummer.py` – LOC: 27, Klassen: 0, Funktionen: 1
  - Imports: datetime, os
- `models/rechnung.py` – LOC: 26, Klassen: 1, Funktionen: 3
  - Imports: datetime, models
- `gui/einstellungen_gui.py` – LOC: 19, Klassen: 0, Funktionen: 1
  - Imports: tkinter
- `gui/kunden_gui.py` – LOC: 19, Klassen: 0, Funktionen: 1
  - Imports: tkinter
- `gui/statistik_gui.py` – LOC: 19, Klassen: 0, Funktionen: 1
  - Imports: tkinter
- `utils/logger.py` – LOC: 19, Klassen: 0, Funktionen: 2
  - Imports: logging, os

### 2.2 requirements.txt
```
defusedxml==0.7.1
fonttools==4.57.0
fpdf2==2.8.3
pillow==11.2.1
```

### 2.3 GUI-/Export-/Test-Indikatoren
- GUI: {'tkinter': 6, 'customtkinter': 0, 'PyQt5': 0, 'PySide6': 0, 'flet': 0, 'kivy': 0, 'ttk': 0, 'qtpy': 0}
- Export: {'reportlab': 0, 'fpdf': 1, 'pdf': 4, 'csv': 3, 'xml': 3}
- Testing: {'pytest': 0, 'unittest': 0}

## 3. Architektur-Bewertung
- **GUI vorhanden:** Ja – dominant: tkinter
- **Exports-Modul:** Ja
- **Logger vorhanden:** Ja
- **Tests vorhanden:** Ja
- **Startdatei (start.py):** Nein

### 3.1 Stärken
- Trennung in `gui/`, `models/`, `exports/`, `utils/`.
- Fonts/Assets versioniert → reproduzierbare PDF-Exports.
- Logs vorhanden → Debug/Diagnose möglich.

### 3.2 Risiken/Verbesserungspotenziale
- Fehlender **Entry-Point** (`start.py`) für GUI-Start & Packaging.
- **Config/Pfade** ggf. verteilt/hardcodiert → zentralisieren (z. B. `config.py`/`config.yaml`).
- **Error-Handling**: zentraler Exception-Handler + user-freundliche Meldungen in der GUI.
- **Tests** ausbauen (Kernlogik, Exportformate) + pre-commit (ruff/mypy/pytest).
- **Persistenz**: JSON/Plaintext ggf. auf SQLite/ORM heben.

## 4. Zielarchitektur (Vorschlag)
```
start.py                # Einstiegspunkt, App-Init, Icon, Logging, Config
app/
  gui/                  # bestehende Views
  models/               # Datenmodelle
  services/             # Rechnungs- & Exportlogik
  utils/                # Logger, Pfad- & Config-Helper
  data/                 # persistente Daten
assets/
  icon.png              # App-Icon

```
**Datenfluss:** GUI → Services → Models/Exports → Datei/DB.

## 5. Konkreter Refactoring-Plan (Priorisiert)
1. Startdatei `start.py` anlegen (GUI-Init, Icon, Logging, Pfade).
2. Zentrales Config-System einführen (env/dev/prod-Profile, Pfade relativ, AppData/~/Library).
3. Services-Schicht extrahieren (Rechnungslogik, Export, Validierung).
4. Error-Handling vereinheitlichen (eigene Exceptions, GUI-Dialoge, Logging).
5. Tests erweitern (pytest): Modelle, Export-Validierung (CSV/XML/PDF).
6. CI/Qualität: ruff (Lint), mypy (Types), pre-commit Hooks.
7. Packaging: PyInstaller (--onefile --windowed --icon=assets/icon.ico).

## 6. Nächste Schritte (sofort umsetzbar)
1) `start.py` erstellen und GUI per Doppelklick startfähig machen.
2) `config.py`/`config.yaml` einführen; alle Pfade zentral.
3) `services/`-Layer für Rechnungslogik & Export.
4) Packaging-Probe mit PyInstaller; Artefakt in `dist/`.