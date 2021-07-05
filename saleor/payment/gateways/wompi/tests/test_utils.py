from decimal import Decimal

from ....interface import AddressData
from ..utils import get_amount_for_wompi, get_amount_from_wompi, shipping_to_wompi_dict


def test_get_amount_for_wompi():
    assert get_amount_for_wompi(Decimal(1)) == 100
    assert get_amount_for_wompi(Decimal(1.2)) == 120


def test_get_amount_from_wompi():
    assert get_amount_from_wompi(100) == Decimal(1)


def test_shipping_address_to_stripe_dict(wompi_address):
    address = wompi_address
    address_data = AddressData(**address.as_data())

    expected_address_dict = {
        "address_line_1": address.street_address_1,
        "address_line_2": address.street_address_2,
        "country": address.country,
        "region": address.city_area,
        "city": address.city,
        "name": address.first_name + " " + address.last_name,
        "phone_number": address.phone,
        "postal_code": address.postal_code,
    }

    assert shipping_to_wompi_dict(address_data) == expected_address_dict
