import os
from decimal import Decimal
from math import isclose
from urllib.request import urlopen

import pytest
import vcr

from .....account.models import Address
from .... import ChargeStatus
from ....interface import AddressData, CustomerSource, GatewayConfig, PaymentMethodInfo
from ....utils import create_payment_information
from .. import TransactionKind, authorize, capture, get_client_token, refund, void
from ..client.wompi_handler import AcceptanceToken

TRANSACTION_AMOUNT = Decimal(4242.42)
TRANSACTION_REFUND_AMOUNT = Decimal(24.24)
TRANSACTION_CURRENCY = "COP"
PAYMENT_METHOD_CARD_SIMPLE = "pm_card_pl"
CARD_SIMPLE_DETAILS = PaymentMethodInfo(
    last_4="0005", exp_year=2020, exp_month=8, brand="visa", type="card"
)
PAYMENT_METHOD_CARD_3D_SECURE = "pm_card_threeDSecure2Required"

# Set to True if recording new cassette with sandbox using credentials in env
RECORD = True


@pytest.fixture()
def gateway_config():
    return GatewayConfig(
        gateway_name="Wompi",
        auto_capture=True,
        supported_currencies="COP",
        connection_params={"public_key": "public", "private_key": "secret",},
    )


@pytest.fixture()
def sandbox_gateway_config(gateway_config):
    if RECORD:
        connection_params = {
            "public_key": os.environ.get("WOMPI_PUBLIC_KEY"),
            "private_key": os.environ.get("WOMPI_SECRET_KEY"),
        }
        gateway_config.connection_params.update(connection_params)
    return gateway_config


@pytest.fixture
def address(db):  # pylint: disable=W0613
    return Address.objects.create(
        first_name="John",
        last_name="Doe",
        company_name="Mirumee Software",
        street_address_1="Tęczowa 7",
        street_address_2="Tęczowa 7",
        city="Bogotá",
        city_area="Cundinamarca",
        postal_code="111111",
        country="CO",
        phone="+48713988102",
    )


@pytest.fixture()
def wompi_payment(payment_dummy):
    payment_dummy.total = TRANSACTION_AMOUNT
    payment_dummy.currency = TRANSACTION_CURRENCY
    return payment_dummy


@pytest.fixture()
def acceptancce_token(sandbox_gateway_config):
    obj = AcceptanceToken(sandbox_gateway_config.connection_params)
    token = obj.send_request()
    return token.acceptance_token


@pytest.mark.integration
def test_authorize(sandbox_gateway_config, wompi_payment, address, acceptancce_token):
    payment_info = create_payment_information(
        wompi_payment,
        PAYMENT_METHOD_CARD_SIMPLE,
        additional_data={"acceptance_token": acceptancce_token},
    )
    payment_info.shipping = AddressData(**address.as_data())
    response = authorize(payment_info, sandbox_gateway_config)
    assert response.is_success is True
    assert response.kind == TransactionKind.CAPTURE
    assert isclose(response.amount, TRANSACTION_AMOUNT)
    assert response.currency == TRANSACTION_CURRENCY
