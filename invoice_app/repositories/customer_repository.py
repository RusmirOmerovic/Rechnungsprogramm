from sqlalchemy import select

from invoice_app.models.customer import Customer


class CustomerRepository:
    def __init__(self, session) -> None:
        self.session = session

    def list_customers(self) -> list[Customer]:
        stmt = select(Customer).order_by(Customer.name.asc())
        return list(self.session.scalars(stmt).all())

    def get_customer(self, customer_id: int) -> Customer | None:
        return self.session.get(Customer, customer_id)

    def create_customer(self, data: dict) -> Customer:
        customer = Customer(**data)
        self.session.add(customer)
        self.session.flush()
        return customer

    def update_customer(self, customer: Customer, data: dict) -> Customer:
        for key, value in data.items():
            setattr(customer, key, value)
        self.session.flush()
        return customer

    def delete_customer(self, customer: Customer) -> None:
        self.session.delete(customer)
        self.session.flush()
