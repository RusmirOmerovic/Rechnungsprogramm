from fpdf import FPDF
from models.rechnung import Rechnung
from models.kunde import Kunde
from models.position import Position

class PDFExporter:
    def __init__(self, rechnung: Rechnung):
        self.rechnung = rechnung
        self.pdf = FPDF()
        self.pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
        self.pdf.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf", uni=True)
        self.pdf.add_page()
        self.pdf.set_font("DejaVu", size=12)


    def add_header(self):
        self.pdf.set_font("DejaVu", "B", 16)
        self.pdf.cell(100, 10, "Rechnung", ln=0)
        self.pdf.set_font("DejaVu", "", 12)
        self.pdf.cell(0, 10, f"Datum: {self.rechnung.datum.strftime('%d.%m.%Y')}", align="R", ln=1)

        self.pdf.set_font("DejaVu", "", 12)
        self.pdf.cell(0, 10, f"Rechnungsnummer: {self.rechnung.nummer}", ln=True)


    def add_kundendaten(self):
        self.pdf.set_xy(10, 30)  # Position im oberen linken Bereich
        self.pdf.cell(0, 6, f"{self.rechnung.kunde.vorname} {self.rechnung.kunde.nachname}", ln=True)
        self.pdf.cell(0, 6, f"{self.rechnung.kunde.strasse}", ln=True)
        self.pdf.cell(0, 6, f"{self.rechnung.kunde.plz} {self.rechnung.kunde.ort}", ln=True)
        self.pdf.ln(10)


    def add_positionen(self):
        self.pdf.ln(5)
        self.pdf.set_font("DejaVu", "B", 12)
        self.pdf.cell(90, 10, "Leistung", border=1)
        self.pdf.cell(30, 10, "Menge", border=1)
        self.pdf.cell(30, 10, "Einzelpreis", border=1)
        self.pdf.cell(30, 10, "Gesamt", border=1, ln=True)
        self.pdf.set_font("DejaVu", "", 12)
        for p in self.rechnung.positionen:
            self.pdf.cell(90, 10, p.beschreibung, border=1)
            self.pdf.cell(30, 10, str(p.menge), border=1)
            self.pdf.cell(30, 10, f"{p.einzelpreis:.2f}€", border=1)
            self.pdf.cell(30, 10, f"{p.gesamtpreis:.2f}€", border=1, ln=True)

    def add_summe(self):
        mwst_satz = 0.19  # 19 % Umsatzsteuer

        netto = self.rechnung.gesamtbetrag
        ust = netto * mwst_satz
        brutto = netto + ust

        self.pdf.ln(5)
        self.pdf.set_font("DejaVu", "", 12)

        def summe_line(label, betrag):
            self.pdf.cell(120)  # Leerraum für Rechtsausrichtung
            self.pdf.cell(40, 8, label, border=0)
            self.pdf.cell(30, 8, f"{betrag:.2f}€", border=0, ln=True)

        summe_line("Nettobetrag:", netto)
        summe_line("Umsatzsteuer (19 %):", ust)
        self.pdf.set_font("DejaVu", "B", 12)
        summe_line("Bruttobetrag:", brutto)


    def export(self, pfad="rechnung.pdf"):
        self.add_header()
        self.add_kundendaten()
        self.add_positionen()
        self.add_summe()
        self.pdf.output(pfad)
