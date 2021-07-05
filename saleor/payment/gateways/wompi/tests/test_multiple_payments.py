import pytest

from ..client.constants import *
from .common import *


@pytest.mark.parametrize("payment_method", VARIOUS_METHODS)
def test_payment_type_method_data_validation(payment_method):
    assert WOMPI_PAYMENT_METHODS.is_valid_payment_data(payment_method) is True

    with pytest.raises(WompiValidationException) as execinfo:
        # Should raise validation error if we pass incomplete keys.
        incomplete_payment_method_data = payment_method.copy()
        type = payment_method.get("type")
        # Deleting the last element of Dict.
        missing_key_name = WOMPI_PAYMENT_METHODS.REQUIRED_FIELDS.get(type)[-1]
        del incomplete_payment_method_data[missing_key_name]
        WOMPI_PAYMENT_METHODS.is_valid_payment_data(incomplete_payment_method_data)

    assert (
        missing_key_name in execinfo.value.args[0]
    ), f"{missing_key_name} not found in exception info."
