from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from invoice_app.database.session import SessionLocal
from invoice_app.repositories.customer_repository import CustomerRepository
from invoice_app.repositories.invoice_repository import InvoiceRepository
from invoice_app.models.invoice_item import InvoiceItem
from invoice_app.services.json_service import JsonService
from invoice_app.services.pdf_service import PdfService


class InvoiceService:
    def __init__(self) -> None:
        self.json_service = JsonService()
        self.pdf_service = PdfService()

    @staticmethod
    def _round(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calculate_item(self, item: dict) -> dict:
        if not item.get("description", "").strip():
            raise ValueError("Beschreibung darf nicht leer sein.")
        quantity = Decimal(str(item.get("quantity", 0)))
        unit_price_net = Decimal(str(item.get("unit_price_net", 0)))
        tax_rate = Decimal(str(item.get("tax_rate", 0)))
        if quantity <= 0:
            raise ValueError("Menge muss > 0 sein.")
        if unit_price_net < 0:
            raise ValueError("Einzelpreis netto muss >= 0 sein.")
        if tax_rate < 0:
            raise ValueError("Steuersatz muss >= 0 sein.")
        line_net = self._round(quantity * unit_price_net)
        line_tax = self._round(line_net * tax_rate / Decimal("100"))
        line_gross = self._round(line_net + line_tax)
        return {**item, "line_net": float(line_net), "line_tax": float(line_tax), "line_gross": float(line_gross)}

    def calculate_totals(self, items: list[dict]) -> dict:
        calc_items = [self.calculate_item(item) for item in items]
        net = sum(Decimal(str(i["line_net"])) for i in calc_items)
        tax = sum(Decimal(str(i["line_tax"])) for i in calc_items)
        gross = sum(Decimal(str(i["line_gross"])) for i in calc_items)
        return {"items": calc_items, "net_total": float(self._round(net)), "tax_total": float(self._round(tax)), "gross_total": float(self._round(gross))}

    def _next_invoice_number(self, repo: InvoiceRepository, invoice_date: date) -> str:
        year = invoice_date.year
        latest = repo.get_last_number_for_year(year)
        seq = int(latest.split("-")[1]) + 1 if latest else 1
        return f"{year}-{seq:04d}"

    def list_invoices(self):
        with SessionLocal() as session:
            return InvoiceRepository(session).list_invoices()

    def create_invoice(self, data: dict):
        customer_id = data.get("customer_id")
        if not customer_id:
            raise ValueError("Kunde muss ausgewählt sein.")
        if not data.get("invoice_date"):
            raise ValueError("Rechnungsdatum darf nicht leer sein.")
        items = data.get("items", [])
        if not items:
            raise ValueError("Mindestens eine Position erforderlich.")

        totals = self.calculate_totals(items)
        with SessionLocal() as session:
            customer_repo = CustomerRepository(session)
            customer = customer_repo.get_customer(customer_id)
            if customer is None:
                raise ValueError("Kunde wurde nicht gefunden.")

            repo = InvoiceRepository(session)
            number = self._next_invoice_number(repo, data["invoice_date"])
            invoice = repo.create_invoice({
                "number": number,
                "customer_id": customer_id,
                "invoice_date": data["invoice_date"],
                "service_period": data.get("service_period"),
                "due_date": data.get("due_date"),
                "net_total": totals["net_total"],
                "tax_total": totals["tax_total"],
                "gross_total": totals["gross_total"],
                "status": data.get("status", "erstellt"),
            })
            for item in totals["items"]:
                session.add(InvoiceItem(invoice_id=invoice.id, **item))

            payload = {
                "invoice_number": number,
                "invoice_date": data["invoice_date"].isoformat(),
                "service_period": data.get("service_period"),
                "due_date": data.get("due_date").isoformat() if data.get("due_date") else None,
                "customer": {
                    "id": customer.id,
                    "customer_number": customer.customer_number,
                    "name": customer.name,
                    "street": customer.street,
                    "postal_code": customer.postal_code,
                    "city": customer.city,
                    "email": customer.email,
                    "phone": customer.phone,
                },
                "items": totals["items"],
                "net_total": totals["net_total"],
                "tax_total": totals["tax_total"],
                "gross_total": totals["gross_total"],
                "status": data.get("status", "erstellt"),
            }
            invoice.json_path = self.json_service.write_invoice_json(payload, number)
            invoice.pdf_path = self.pdf_service.create_invoice_pdf(payload, number)
            session.commit()
            session.refresh(invoice)
            return invoice
