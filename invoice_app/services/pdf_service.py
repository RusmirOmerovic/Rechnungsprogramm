from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class PdfService:
    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parents[2] / "daten" / "invoices_pdf"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_invoice_pdf(self, payload: dict, invoice_number: str) -> str:
        path = self.base_dir / f"{invoice_number}.pdf"
        c = canvas.Canvas(str(path), pagesize=A4)
        y = 800
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, y, "Rechnung")
        y -= 30
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"Rechnungsnummer: {payload['invoice_number']}")
        y -= 18
        c.drawString(50, y, f"Datum: {payload['invoice_date']}")
        y -= 30
        customer = payload["customer"]
        c.drawString(50, y, f"Kunde: {customer['name']}")
        y -= 16
        c.drawString(50, y, f"Adresse: {customer.get('street','')}, {customer.get('postal_code','')} {customer.get('city','')}")
        y -= 24
        c.drawString(50, y, "Positionen:")
        y -= 16
        for item in payload["items"]:
            c.drawString(50, y, f"{item['description']} | {item['quantity']} {item['unit']} x {item['unit_price_net']}€ | MwSt {item['tax_rate']}% | {item['line_gross']}€")
            y -= 16
        y -= 20
        c.drawString(50, y, f"Netto: {payload['net_total']} €")
        y -= 16
        c.drawString(50, y, f"Steuer: {payload['tax_total']} €")
        y -= 16
        c.drawString(50, y, f"Brutto: {payload['gross_total']} €")
        y -= 20
        c.drawString(50, y, f"Zahlungsziel: {payload['due_date']}")
        c.save()
        return str(path)
