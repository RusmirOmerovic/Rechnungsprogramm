from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from invoice_app.database.session import SessionLocal
from invoice_app.repositories.customer_repository import CustomerRepository
from invoice_app.repositories.invoice_repository import InvoiceRepository
from invoice_app.models.invoice_item import InvoiceItem
from invoice_app.services.json_service import JsonService
from invoice_app.services.pdf_service import PdfService


class InvoiceValidationError(ValueError):
    def __init__(self, field: str, message: str) -> None:
        super().__init__(message)
        self.field = field


def _format_service_date(value: date) -> str:
    return f"{value.day:02d}.{value.month:02d}.{value.year:04d}"


def normalize_service_period(data: dict) -> str | None:
    """Normalize new date inputs without changing the payload or legacy text."""
    if "service_period_mode" not in data:
        legacy = data.get("service_period")
        if legacy is not None and not isinstance(legacy, str):
            raise InvoiceValidationError("service_period_mode", "Leistungsangabe muss Text sein.")
        return legacy

    mode = data["service_period_mode"]
    start = data.get("service_date_from")
    end = data.get("service_date_to")
    if mode not in ("none", "single", "range"):
        raise InvoiceValidationError("service_period_mode", "Bitte einen gültigen Leistungsmodus wählen.")
    if mode == "none":
        if start is not None or end is not None:
            raise InvoiceValidationError("service_period_mode", "Bei 'Keine Angabe' dürfen keine Leistungsdaten übergeben werden.")
        return None
    # datetime and strings are deliberately not accepted as date-only inputs.
    if type(start) is not date:
        raise InvoiceValidationError("service_date_from", "Bitte ein gültiges Leistungsdatum (Von) wählen.")
    if mode == "single":
        if end is not None:
            raise InvoiceValidationError("service_date_to", "Ein einzelnes Leistungsdatum darf kein Bis-Datum enthalten.")
        return _format_service_date(start)
    if type(end) is not date:
        raise InvoiceValidationError("service_date_to", "Bitte ein gültiges Leistungsdatum (Bis) wählen.")
    if end < start:
        raise InvoiceValidationError("service_date_to", "Das Bis-Datum darf nicht vor dem Von-Datum liegen.")
    return f"{_format_service_date(start)} - {_format_service_date(end)}"


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
            raise InvoiceValidationError("customer_id", "Bitte einen Kunden auswählen.")
        if type(data.get("invoice_date")) is not date:
            raise InvoiceValidationError("invoice_date", "Bitte ein gültiges Rechnungsdatum wählen.")
        if data.get("due_date") is not None and type(data["due_date"]) is not date:
            raise InvoiceValidationError("due_date", "Bitte ein gültiges Zahlungsziel wählen.")
        service_period = normalize_service_period(data)
        items = data.get("items", [])
        if not items:
            raise InvoiceValidationError("items", "Mindestens eine Position erforderlich. Bitte eine Position hinzufügen.")

        try:
            totals = self.calculate_totals(items)
        except ValueError as error:
            raise InvoiceValidationError("items", str(error)) from error
        with SessionLocal() as session:
            customer_repo = CustomerRepository(session)
            customer = customer_repo.get_customer(customer_id)
            if customer is None:
                raise InvoiceValidationError("customer_id", "Kunde wurde nicht gefunden. Bitte die Kundenauswahl prüfen.")

            repo = InvoiceRepository(session)
            number = self._next_invoice_number(repo, data["invoice_date"])
            invoice = repo.create_invoice({
                "number": number,
                "customer_id": customer_id,
                "invoice_date": data["invoice_date"],
                "service_period": service_period,
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
                "service_period": service_period,
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
            # Only this session: return loaded values without a fallible SELECT
            # after a successful commit. No global session configuration changes.
            session.expire_on_commit = False
            session.commit()
            return invoice
