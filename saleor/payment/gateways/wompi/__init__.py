# The list of currencies supported by Wompi
SUPPORTED_CURRENCIES = ("COP",)

import uuid
from typing import Optional

from ... import TransactionKind
from ...interface import GatewayConfig, GatewayResponse, PaymentData, PaymentMethodInfo
from .client.wompi_handler import WompiHandler
from .utils import get_amount_for_wompi


def get_client_token(**_):
    return str(uuid.uuid4())


def authorize(
    payment_information: PaymentData, config: GatewayConfig
) -> GatewayResponse:
    stripe_amount = get_amount_for_wompi(payment_information.amount)
    future_use = "off_session" if config.store_customer else "on_session"
    customer_id = PaymentData.customer_id if payment_information.reuse_source else None

    pass


def capture(payment_information: PaymentData, config: GatewayConfig) -> GatewayResponse:
    intent = None
    return GatewayResponse()


def confirm(payment_information: PaymentData, config: GatewayConfig) -> GatewayResponse:
    return GatewayResponse()


def refund(payment_information: PaymentData, config: GatewayConfig) -> GatewayResponse:
    return GatewayResponse()


def void(payment_information: PaymentData, config: GatewayConfig) -> GatewayResponse:
    return GatewayResponse()


# def list_client_sources(
#         config: GatewayConfig, customer_id: str
# ) -> List[CustomerSource]:
#     pass


def process_payment(
    payment_information: PaymentData, config: GatewayConfig
) -> GatewayResponse:
    return GatewayResponse()
