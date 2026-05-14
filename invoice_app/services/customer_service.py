from invoice_app.database.session import SessionLocal
from invoice_app.repositories.customer_repository import CustomerRepository


class CustomerService:
    @staticmethod
    def _clean(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    def _validate(self, data: dict) -> None:
        if not data.get("name"):
            raise ValueError("Name darf nicht leer sein.")
        if not data.get("customer_number"):
            raise ValueError("Kundennummer darf nicht leer sein.")

        email = data.get("email")
        if email and "@" not in email:
            raise ValueError("E-Mail muss ein @ enthalten.")

        postal_code = data.get("postal_code")
        if postal_code and not postal_code.isdigit():
            raise ValueError("PLZ darf nur Zahlen enthalten.")

    def _normalize_payload(self, data: dict) -> dict:
        payload = {
            "customer_number": self._clean(data.get("customer_number")) or "",
            "name": self._clean(data.get("name")) or "",
            "street": self._clean(data.get("street")),
            "postal_code": self._clean(data.get("postal_code")),
            "city": self._clean(data.get("city")),
            "email": self._clean(data.get("email")),
            "phone": self._clean(data.get("phone")),
        }
        self._validate(payload)
        return payload

    def list_customers(self):
        with SessionLocal() as session:
            repo = CustomerRepository(session)
            return repo.list_customers()

    def get_customer(self, customer_id: int):
        with SessionLocal() as session:
            repo = CustomerRepository(session)
            return repo.get_customer(customer_id)

    def create_customer(self, data: dict):
        payload = self._normalize_payload(data)
        with SessionLocal() as session:
            repo = CustomerRepository(session)
            customer = repo.create_customer(payload)
            session.commit()
            session.refresh(customer)
            return customer

    def update_customer(self, customer_id: int, data: dict):
        payload = self._normalize_payload(data)
        with SessionLocal() as session:
            repo = CustomerRepository(session)
            customer = repo.get_customer(customer_id)
            if customer is None:
                raise ValueError("Kunde wurde nicht gefunden.")
            updated = repo.update_customer(customer, payload)
            session.commit()
            session.refresh(updated)
            return updated

    def delete_customer(self, customer_id: int):
        with SessionLocal() as session:
            repo = CustomerRepository(session)
            customer = repo.get_customer(customer_id)
            if customer is None:
                raise ValueError("Kunde wurde nicht gefunden.")
            repo.delete_customer(customer)
            session.commit()
