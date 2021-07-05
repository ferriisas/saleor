from decimal import Decimal
from typing import Dict

from ...interface import AddressData


def get_amount_for_wompi(amount):
    # Multiply by 100 for non-zero-decimal currencies
    # Amount should be return in cents.
    amount *= 100

    # Using int(Decimal) directly may yield wrong result
    # such as int(Decimal(24.24)*100) will equal to 2423
    return int(amount.to_integral_value())


def get_amount_from_wompi(amount):
    """Get appropriate amount from Wompi."""
    amount = Decimal(amount)
    amount /= Decimal(100)
    return amount


def shipping_to_wompi_dict(shipping: AddressData) -> Dict:
    return {
        "address_line_1": shipping.street_address_1,
        "address_line_2": shipping.street_address_2,
        "country": shipping.country,
        "region": shipping.city_area,
        "city": shipping.city,
        "name": shipping.first_name + " " + shipping.last_name,
        "phone_number": shipping.phone,
        "postal_code": shipping.postal_code,
    }
