import pytest

from invoice_app.services.customer_service import CustomerService


@pytest.fixture
def service() -> CustomerService:
    return CustomerService()


def test_valid_customer_is_accepted(service: CustomerService) -> None:
    payload = service._normalize_payload(
        {
            "customer_number": "K-1001",
            "name": "Max Mustermann",
            "email": "max@example.com",
            "postal_code": "12345",
        }
    )

    assert payload["customer_number"] == "K-1001"
    assert payload["name"] == "Max Mustermann"
    assert payload["email"] == "max@example.com"
    assert payload["postal_code"] == "12345"


def test_empty_name_is_rejected(service: CustomerService) -> None:
    with pytest.raises(ValueError, match="Name darf nicht leer sein"):
        service._normalize_payload({"customer_number": "K-1002", "name": "   "})


def test_empty_customer_number_is_rejected(service: CustomerService) -> None:
    with pytest.raises(ValueError, match="Kundennummer darf nicht leer sein"):
        service._normalize_payload({"customer_number": "", "name": "Firma GmbH"})


def test_invalid_email_is_rejected(service: CustomerService) -> None:
    with pytest.raises(ValueError, match="E-Mail muss ein @ enthalten"):
        service._normalize_payload(
            {
                "customer_number": "K-1003",
                "name": "Firma GmbH",
                "email": "ungueltig.example.com",
            }
        )


def test_invalid_postal_code_is_rejected(service: CustomerService) -> None:
    with pytest.raises(ValueError, match="PLZ darf nur Zahlen enthalten"):
        service._normalize_payload(
            {
                "customer_number": "K-1004",
                "name": "Firma GmbH",
                "postal_code": "12A45",
            }
        )
