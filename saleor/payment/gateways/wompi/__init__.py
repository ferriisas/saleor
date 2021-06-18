# The list of currencies supported by Wompi
SUPPORTED_CURRENCIES = ("COP",)

import uuid
from typing import Optional

from ... import TransactionKind
from ...interface import GatewayConfig, GatewayResponse, PaymentData, PaymentMethodInfo
from .client.wompi_handler import Transaction, WompiHandler
from .utils import get_amount_for_wompi


def get_client_token(**_):
    return str(uuid.uuid4())


def process_payment(
    payment_information: PaymentData, config: GatewayConfig
) -> GatewayResponse:
    return _success_response("")


def authorize(
    payment_information: PaymentData, config: GatewayConfig
) -> GatewayResponse:
    amount = get_amount_for_wompi(payment_information.amount)
    try:
        payload = {
            "acceptance_token": payment_information.data.get("acceptance_token"),
            "amount_in_cents": amount,
            "currency": "COP",
            "customer_email": payment_information.customer_email,
            "reference": payment_information.graphql_payment_id,
            "payment_method": {"type": "NEQUI", "phone_number": "3107654321"},
        }
        conf = config.connection_params
        tran_obj = Transaction(conf)
        response = tran_obj.generate_transaction(payload)
        return _success_response(response)
    except Exception as exc:
        return _error_response(exc)


def capture(payment_information: PaymentData, config: GatewayConfig) -> GatewayResponse:
    intent = None
    return _success_response("")


def confirm(payment_information: PaymentData, config: GatewayConfig) -> GatewayResponse:
    return _success_response("")


def refund(payment_information: PaymentData, config: GatewayConfig) -> GatewayResponse:
    return _success_response("")


def void(payment_information: PaymentData, config: GatewayConfig) -> GatewayResponse:
    return _success_response("")


# def list_client_sources(
#         config: GatewayConfig, customer_id: str
# ) -> List[CustomerSource]:
#     pass


def _error_response(
    kind: str,  # use TransactionKind class
    exc,
    payment_info: PaymentData,
    action_required: bool = False,
) -> GatewayResponse:
    return GatewayResponse(
        is_success=False,
        action_required=action_required,
        transaction_id=payment_info.token,
        amount=payment_info.amount,
        currency=payment_info.currency,
        error=exc.user_message,
        kind=kind,
        raw_response=exc.json_body or {},
        customer_id=payment_info.customer_id,
    )


def _success_response(
    intent,
    kind: str,  # use TransactionKind class
    success: bool = True,
    amount=None,
    currency=None,
    customer_id=None,
    raw_response=None,
):
    return GatewayResponse(
        is_success=success,
        action_required=intent.status == "requires_action",
        transaction_id=intent.id,
        amount=amount,
        currency="COP",
        error=None,
        kind=kind,
        raw_response=raw_response or intent,
        customer_id=customer_id,
    )
