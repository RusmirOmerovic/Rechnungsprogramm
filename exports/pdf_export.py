from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

def rechnung_als_pdf_speichern(produkte, kundendaten, rechnungsnummer, rechnungsdatum, dateiname="rechnung.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf")
    pdf.set_font("DejaVu", size=12)

    # Logo oben rechts
    try:
        logo_breite = 33
        abstand_rechts = 10
        pdf.image("Logo.svg", x=210 - logo_breite - abstand_rechts, y=8, w=logo_breite)
    except FileNotFoundError:
        print("⚠️ Logo nicht gefunden. PDF wird ohne Logo erstellt.")

    # Datum oben rechts neben dem Logo
    pdf.set_xy(10, 10)
    pdf.set_font("DejaVu", size=10)
    pdf.cell(0, 10, f"Datum: {rechnungsdatum}", align="R", ln=True)

    # Kundendaten / Adresse
    pdf.set_xy(10, 50)
    pdf.set_font("DejaVu", size=10)
    pdf.multi_cell(0, 5, kundendaten)

    # Titel
    pdf.set_xy(10, 90)
    pdf.set_font("DejaVu", size=16)
    pdf.cell(0, 10, "🧾 Rechnung", ln=True)

    # Rechnungsnummer direkt unter dem Titel
    pdf.set_font("DejaVu", size=10)
    pdf.cell(0, 10, f"Rechnungsnummer: {rechnungsnummer}", ln=True)

    pdf.ln(5)

    # Tabelle
    pdf.set_font("DejaVu", size=10)
    pdf.cell(40, 10, "Produkt", border=1)
    pdf.cell(30, 10, "Preis", border=1)
    pdf.cell(25, 10, "Menge", border=1)
    pdf.cell(30, 10, "Gesamt", border=1)
    pdf.cell(30, 10, "MwSt (%)", border=1)
    pdf.cell(35, 10, "Steuerbetrag", border=1)
    pdf.ln()

    netto_summe = 0
    steuer_summe = 0
    brutto_summe = 0

    for produkt, preis, menge, steuersatz in produkte:
        gesamt = preis * menge
        steuer_betrag = gesamt * (steuersatz / 100)
        brutto = gesamt + steuer_betrag

        pdf.cell(40, 10, produkt, border=1)
        pdf.cell(30, 10, f"{preis:.2f} €", border=1)
        pdf.cell(25, 10, str(menge), border=1)
        pdf.cell(30, 10, f"{gesamt:.2f} €", border=1)
        pdf.cell(30, 10, f"{steuersatz}%", border=1)
        pdf.cell(35, 10, f"{steuer_betrag:.2f} €", border=1)
        pdf.ln()

        netto_summe += gesamt
        steuer_summe += steuer_betrag
        brutto_summe += brutto

    pdf.ln(5)
    pdf.cell(200, 10, text=f"Nettosumme: {netto_summe:.2f} €", ln=True)
    pdf.cell(200, 10, text=f"Gesamte MwSt: {steuer_summe:.2f} €", ln=True)
    pdf.cell(200, 10, text=f"Bruttosumme: {brutto_summe:.2f} €", ln=True)

    os.makedirs(os.path.dirname(dateiname), exist_ok=True)
    pdf.output(name=dateiname)
