import csv
from pathlib import Path

from models.rechnung import Rechnung

from . import EXPORT_DIR
from .export_utils import DEFAULT_STEUERSATZ, rechnung_zu_exportpositionen


def rechnung_als_csv_speichern(
    rechnung: Rechnung,
    dateiname: str | None = None,
    steuersatz: float = DEFAULT_STEUERSATZ,
) -> Path:
    export_positionen = rechnung_zu_exportpositionen(rechnung, steuersatz)

    ziel_datei = dateiname or f"rechnung_{rechnung.nummer}.csv"
    pfad = Path(ziel_datei)
    if not pfad.is_absolute():
        pfad = EXPORT_DIR / pfad

    pfad.parent.mkdir(parents=True, exist_ok=True)

    with pfad.open(mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Produkt", "Preis", "Menge", "Gesamt", "Steuersatz (%)", "Steuerbetrag (€)"])

        for position in export_positionen:
            writer.writerow(
                [
                    position.beschreibung,
                    f"{position.einzelpreis:.2f}",
                    position.menge,
                    f"{position.gesamt:.2f}",
                    position.steuersatz,
                    f"{position.steuerbetrag:.2f}",
                ]
            )

    return pfad
