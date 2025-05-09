from kunde import Kunde
from position import Position
from rechnung import Rechnung

kunde = Kunde("Max", "Mustermann", "Hauptstraße 1", "12345", "Musterstadt")
position1 = Position("Webdesign", 5, 80.00)
position2 = Position("Beratung", 2, 100.00)

rechnung = Rechnung("2025-001", kunde, [position1, position2])
print(rechnung)
