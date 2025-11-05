import xml.etree.ElementTree as ET
from pathlib import Path

from models.rechnung import Rechnung

from . import EXPORT_DIR
from .export_utils import DEFAULT_STEUERSATZ, rechnung_zu_exportpositionen


def rechnung_als_xml_speichern(
    rechnung: Rechnung,
    dateiname: str | None = None,
    steuersatz: float = DEFAULT_STEUERSATZ,
) -> Path:
    export_positionen = rechnung_zu_exportpositionen(rechnung, steuersatz)

    wurzel = ET.Element("rechnung")
    ET.SubElement(wurzel, "nummer").text = str(rechnung.nummer)
    ET.SubElement(wurzel, "datum").text = rechnung.datum.isoformat()

    kunde_element = ET.SubElement(wurzel, "kunde")
    ET.SubElement(kunde_element, "vorname").text = rechnung.kunde.vorname
    ET.SubElement(kunde_element, "nachname").text = rechnung.kunde.nachname
    ET.SubElement(kunde_element, "strasse").text = rechnung.kunde.strasse
    ET.SubElement(kunde_element, "plz").text = rechnung.kunde.plz
    ET.SubElement(kunde_element, "ort").text = rechnung.kunde.ort

    positionen_element = ET.SubElement(wurzel, "positionen")
    for position in export_positionen:
        position_element = ET.SubElement(positionen_element, "position")
        ET.SubElement(position_element, "beschreibung").text = position.beschreibung
        ET.SubElement(position_element, "einzelpreis").text = f"{position.einzelpreis:.2f}"
        ET.SubElement(position_element, "menge").text = str(position.menge)
        ET.SubElement(position_element, "gesamt").text = f"{position.gesamt:.2f}"
        ET.SubElement(position_element, "steuersatz").text = f"{position.steuersatz}%"
        ET.SubElement(position_element, "steuerbetrag").text = f"{position.steuerbetrag:.2f}"

    tree = ET.ElementTree(wurzel)

    ziel_datei = dateiname or f"rechnung_{rechnung.nummer}.xml"
    pfad = Path(ziel_datei)
    if not pfad.is_absolute():
        pfad = EXPORT_DIR / pfad

    pfad.parent.mkdir(parents=True, exist_ok=True)
    tree.write(pfad, encoding="utf-8", xml_declaration=True)
    return pfad
