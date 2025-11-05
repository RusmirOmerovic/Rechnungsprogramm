from dataclasses import dataclass
from typing import Iterable

from models.position import Position
from models.rechnung import Rechnung

DEFAULT_STEUERSATZ = 19.0


@dataclass(frozen=True)
class ExportPosition:
    beschreibung: str
    einzelpreis: float
    menge: int
    steuersatz: float

    @property
    def gesamt(self) -> float:
        return self.einzelpreis * self.menge

    @property
    def steuerbetrag(self) -> float:
        return self.gesamt * (self.steuersatz / 100)


def _iter_positionen(positionen: Iterable[Position], steuersatz: float) -> list[ExportPosition]:
    export_positionen: list[ExportPosition] = []
    for position in positionen:
        export_positionen.append(
            ExportPosition(
                beschreibung=position.beschreibung,
                einzelpreis=float(position.einzelpreis),
                menge=int(position.menge),
                steuersatz=steuersatz,
            )
        )
    return export_positionen


def rechnung_zu_exportpositionen(rechnung: Rechnung, steuersatz: float = DEFAULT_STEUERSATZ) -> list[ExportPosition]:
    return _iter_positionen(rechnung.positionen, steuersatz)
