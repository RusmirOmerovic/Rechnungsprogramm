from models.kunde import Kunde
from models.position import Position
from models.rechnung import Rechnung
from models.errors import InvalidPositionError
from rechnungsnummer import lese_und_aktualisiere_rechnungsnummer
from exports.csv_export import rechnung_als_csv_speichern
from exports.xml_export import rechnung_als_xml_speichern

try:
    fehlerhafte_position = Position("Support", -5, 120.0)
except InvalidPositionError as e:
    print("❌ Erwarteter Fehler abgefangen:", e)


# Test gültige Position
try:
    p1 = Position("Webdesign", 5, 80.0)
    print("✅ Gültige Position erfolgreich erstellt:", p1)
except Exception as e:  
    print("❌ Fehler:", e)

# Test ungültige Position
try:
    p2 = Position("Support", -3, 100.0)  # ungültige Menge
except Exception as e:
    print("❌ Erwarteter Fehler:", e)


kunde = Kunde("Max", "Mustermann", "Hauptstraße 1", "12345", "Musterstadt")
position1 = Position("Webdesign", 5, 80.00)
position2 = Position("Beratung", 2, 100.00)

rechnungsnummer = lese_und_aktualisiere_rechnungsnummer()
rechnung = Rechnung(rechnungsnummer, kunde, [position1, position2])
print(rechnung)


from exports.pdf_export import PDFExporter

pdf_export = PDFExporter(rechnung)
pdf_path = pdf_export.export("test_rechnung.pdf")
csv_path = rechnung_als_csv_speichern(rechnung, "test_rechnung.csv")
xml_path = rechnung_als_xml_speichern(rechnung, "test_rechnung.xml")

print("📄 Exportierte Dateien:")
print("  PDF:", pdf_path)
print("  CSV:", csv_path)
print("  XML:", xml_path)
