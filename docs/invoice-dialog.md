# Rechnung erfassen

- **Kunde (Pflichtfeld)** bewusst auswählen; auch bei nur einem Kunden bleibt
  zunächst „Bitte Kunden auswählen“ stehen. Ein fehlender Kunde wird direkt am
  Feld mit Text, Fokus und Umrandung angezeigt.
- Positionen wie bisher über **Position hinzufügen** übernehmen. Noch nicht
  hinzugefügte Positionseingaben sind keine Rechnungspositionen.
- **Leistungsangabe**: „Keine Angabe“ (Standard), „Einzelnes Datum“ oder
  „Zeitraum“. Datumsfelder öffnen einen Kalender und zeigen `dd.MM.yyyy`.
  Bei einem Zeitraum sind gleiche Grenzen erlaubt; „Bis“ darf nicht vor „Von“
  liegen. Ausgeblendete Datumswerte werden nicht übergeben.
- **Speichern** bzw. Enter speichert vor dem Schließen. Bei Fehlern bleiben
  derselbe Dialog, alle Formulardaten, Positionen und Positionseingaben erhalten.
  Nach Korrektur kann erneut gespeichert werden. Während des Aufrufs und nach
  Erfolg ist eine weitere Speicherung aus diesem Dialog gesperrt.
- **Abbrechen**, Escape und Fensterschließen speichern nichts. Nach erfolgreicher
  Speicherung aktualisiert die Seite nur die Liste. Ein Listenfehler wird
  ausdrücklich als solcher gemeldet: nur aktualisieren, nicht erneut erstellen.

## Service-Kompatibilität

Neue Aufrufer übergeben `service_period_mode` (`none`, `single`, `range`) und
`service_date_from` / `service_date_to` als Python-`date` oder `None`:

| Modus | Von | Bis | Gespeicherter Text |
| --- | --- | --- | --- |
| none | None | None | None |
| single | 24.09.2026 | None | 24.09.2026 |
| range | 01.09.2026 | 30.09.2026 | 01.09.2026 - 30.09.2026 |

Die reine Service-Normalisierung prüft diese Angaben vor DB- und Exportzugriffen.
Unbekannte Modi, fehlende Datumswerte und widersprüchliche Werte werden abgelehnt.
Ist der neue Modus vorhanden, hat er Vorrang; es gibt keinen Freitext-Fallback.
Fehlt er, bleibt `service_period` als `str` oder `None` unverändert kompatibel
(z. B. „September 2026“). Das Eingabe-Dictionary wird nicht verändert.

SQLite und JSON verwenden denselben Text; das PDF zeigt ihn als „Leistung: …“
nur bei vorhandener Angabe. Bewusste Textspeicherung ohne neue DB-Spalten oder
Migration; strukturierte Datumsabfragen sind nicht Bestandteil dieser Änderung.

## Speichergrenzen

Bei Fehlern vor Commit rollt das Schließen der Service-Session die neuen
DB-Schreibvorgänge zurück. JSON/PDF entstehen weiterhin vor dem Commit und sind
nicht Teil der SQLite-Transaktion: bei einem Export- oder Commitfehler können
unvollständige oder verwaiste Exportdateien zurückbleiben. Es gibt keine
automatische Dateilöschung. Ein erneuter Versuch kann solche Dateien unter der
erneut vergebenen, noch nicht persistierten Rechnungsnummer überschreiben.
Dateien bereits gespeicherter Rechnungen werden dabei nicht gelöscht.

Nur die Session dieses Erstellungsvorgangs nutzt `expire_on_commit=False`.
Der frühere `refresh()` nach Commit entfällt; geladene Rückgabewerte benötigen
keinen weiteren Datenbankzugriff, der einen Erfolg als Fehler erscheinen ließe.
Keine globale Session-Änderung, keine automatischen Wiederholungen, keine
allgemeine Crash-/Idempotenzgarantie. Bei einem Prozessabbruch oder unklarem
Commit-Ausgang zuerst den Rechnungsbestand prüfen, bevor neu erfasst wird.

## Lokale Abnahme (macOS)

1. `python main.py` starten und eine neue Rechnung öffnen. Ohne Kunde speichern:
   Feldhinweis, Fokus und erhaltene Eingaben prüfen; auch in Hell-/Dunkeldarstellung.
2. Kunden wählen, mit gültigem Rechnungsdatum ohne Position speichern:
   Fehlermeldung und unveränderte Eingaben prüfen.
3. Position hinzufügen; zusätzliche Positionseingaben ungespeichert eintippen.
   Einen umgekehrten Leistungszeitraum speichern: Dialog bleibt offen.
4. Zeitraum korrigieren und einmal speichern: Dialog schließt, genau eine neue
   Rechnung erscheint. Einzeldatum, gleiche Grenzen und „Keine Angabe“ ebenfalls
   in separaten Testrechnungen prüfen.
5. Leistungsangabe in SQLite, JSON und PDF vergleichen. Ohne Angabe darf keine
   Leistungszeile im PDF erscheinen. Kalender, Tab-Reihenfolge, Enter, Escape
   und Abbrechen prüfen. Tests mit einer separaten Testdatenbank durchführen.

Automatisierte Regressionstests simulieren zusätzlich Export-/Commitfehler und
Listenfehler. Die visuelle macOS-Abnahme bleibt beim Product Owner.
