import os
import xml.etree.ElementTree as ET

def rechnung_als_xml_speichern(produkte, dateiname="rechnung.xml"):
    rechnung = ET.Element("rechnung")

    for produkt, preis, menge, steuersatz in produkte:
        position = ET.SubElement(rechnung, "position")
        ET.SubElement(position, "produktname").text = produkt
        ET.SubElement(position, "preis").text = f"{preis:.2f}"
        ET.SubElement(position, "menge").text = str(menge)
        ET.SubElement(position, "gesamt").text = f"{preis * menge:.2f}"
        ET.SubElement(position, "steuersatz").text = f"{steuersatz}%"
        ET.SubElement(position, "steuerbetrag").text = f"{preis * menge * steuersatz / 100:.2f}"

    tree = ET.ElementTree(rechnung)
    os.makedirs(os.path.dirname(dateiname), exist_ok=True)
    tree.write(dateiname, encoding="utf-8", xml_declaration=True)
