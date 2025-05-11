from models.kunde import Kunde
from models.position import Position
from models.rechnung import Rechnung
from models.errors import InvalidPositionError

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

rechnung = Rechnung("2025-001", kunde, [position1, position2])
print(rechnung)


from exports.pdf_export import PDFExporter

pdf_export = PDFExporter(rechnung)
pdf_export.export("tests/test_rechnung.pdf")
