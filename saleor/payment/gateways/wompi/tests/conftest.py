from unittest import mock

import pytest

from .....account.models import Address
from .....checkout import calculations
from .....plugins.manager import get_plugins_manager
from .... import TransactionKind
from ....interface import GatewayConfig
from ....models import Checkout, Transaction
from ....utils import create_payment
from ..plugin import WompiGatewayPlugin
from .common import *


@pytest.fixture
def wompi_plugin(settings):
    def fun(api_key=None, api_secret=None, api_event=None, is_sandbox=True):
        api_key = api_key or "test_key"
        api_secret = api_secret or "test_secret"
        settings.PLUGINS = ["saleor.payment.gateways.wompi.plugin.WompiGatewayPlugin"]
        manager = get_plugins_manager()

        with mock.patch(
            "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
        ):
            manager.save_plugin_configuration(
                WompiGatewayPlugin.PLUGIN_ID,
                {
                    "active": True,
                    "configuration": [
                        {"name": "Sandbox Public API key", "value": api_key},
                        {"name": "Sandbox Secret API key", "value": api_secret},
                        {"name": "Sandbox Event API key", "value": api_event},
                        {"name": "Public API key", "value": api_key},
                        {"name": "Secret API key", "value": api_secret},
                        {"name": "Event API key", "value": api_event},
                        {"name": "Use sandbox", "value": is_sandbox},
                        {"name": "Store customers card", "value": False},
                        {"name": "Automatic payment capture", "value": True},
                        {"name": "Supported currencies", "value": False},
                    ],
                },
            )

        manager = get_plugins_manager()
        return manager.plugins[0]

    return fun


@pytest.fixture
def payment_wompi_for_checkout(checkout_with_items, address, shipping_method):
    checkout_with_items.billing_address = address
    checkout_with_items.shipping_address = address
    checkout_with_items.shipping_method = shipping_method
    checkout_with_items.save()
    total = calculations.calculate_checkout_total_with_gift_cards(
        checkout=checkout_with_items
    )
    payment = create_payment(
        gateway=WompiGatewayPlugin.PLUGIN_ID,
        payment_token="",
        total=total.gross.amount,
        currency=checkout_with_items.currency,
        email=checkout_with_items.email,
        customer_ip_address="",
        checkout=checkout_with_items,
        return_url="https://www.example.com",
    )
    return payment


@pytest.fixture
def payment_wompi_for_order(payment_wompi_for_checkout, order_with_lines):
    payment_wompi_for_checkout.checkout = None
    payment_wompi_for_checkout.order = order_with_lines
    payment_wompi_for_checkout.save()

    Transaction.objects.create(
        payment=payment_wompi_for_checkout,
        action_required=False,
        kind=TransactionKind.AUTH,
        token="token",
        is_success=True,
        amount=order_with_lines.total_gross_amount,
        currency=order_with_lines.currency,
        error="",
        gateway_response={},
        action_required_data={},
    )
    return payment_wompi_for_checkout


@pytest.fixture()
def gateway_config():
    return GatewayConfig(
        gateway_name="Wompi",
        auto_capture=True,
        supported_currencies="COP",
        connection_params={
            "public_key": "public",
            "private_key": "secret",
            "event_key": "event_key",
        },
    )


@pytest.fixture()
def sandbox_gateway_config(gateway_config):
    connection_params = {
        "public_key": "test_public_key",
        "private_key": "test_private_key",
        "event_key": "test_event_key",
    }
    gateway_config.connection_params.update(connection_params)
    return gateway_config


@pytest.fixture
def wompi_address(db):  # pylint: disable=W0613
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
    payment_dummy.gateway = WompiGatewayPlugin.PLUGIN_ID
    return payment_dummy


@pytest.fixture
def acceptance_token(sandbox_gateway_config):
    response = read_json("acceptance_token.json")
    return response["data"]["presigned_acceptance"]["acceptance_token"]
