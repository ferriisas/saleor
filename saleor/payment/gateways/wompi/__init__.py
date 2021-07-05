# The list of currencies supported by Wompi
SUPPORTED_CURRENCIES = ("COP",)
import logging
import uuid

from ... import TransactionKind
from ...interface import GatewayConfig, GatewayResponse, PaymentData, PaymentMethodInfo
from .client.constants import WOMPI_PAYMENT_METHODS
from .client.wompi_handler import TransactionRequest, TransactionStates, WompiHandler
from .utils import get_amount_for_wompi, get_amount_from_wompi, shipping_to_wompi_dict

logger = logging.getLogger(__name__)


def get_client_token(**_):
    return str(uuid.uuid4())


def extract_payment_method(payment_information: PaymentData):
    return (
        payment_information.data.get("payment_method")
        or payment_information.data.get("paymentMethod")
        or {}
    )


def authorize(
    payment_information: PaymentData, config: GatewayConfig
) -> GatewayResponse:
    amount = get_amount_for_wompi(payment_information.amount)
    kind = TransactionKind.AUTH
    # Accept data in both keys: payment_method or paymentMethod
    payment_method = extract_payment_method(payment_information)
    try:
        payload = {
            "acceptance_token": payment_information.data.get("acceptance_token"),
            "amount_in_cents": amount,
            "currency": payment_information.currency,
            "customer_email": payment_information.customer_email,
            "reference": payment_information.graphql_payment_id,
            "payment_method": payment_method,
            "shipping_address": (
                shipping_to_wompi_dict(payment_information.shipping)
                if payment_information.shipping
                else None
            ),
        }
        conf = config.connection_params
        tran_obj = TransactionRequest(conf)
        gateway_resp = tran_obj.generate(payload)
        response = _success_response(gateway_resp, kind=kind, success=True)
    except Exception as exc:
        response = _error_response(kind, exc, payment_information)
    return response


def process_payment(
    payment_information: PaymentData, config: GatewayConfig
) -> GatewayResponse:
    return authorize(payment_information, config)


def capture(payment_information: PaymentData, config: GatewayConfig) -> GatewayResponse:
    try:
        conf = config.connection_params
        tran_obj = TransactionRequest(conf)
        response = tran_obj.retrieve(payment_information.token)
        return _success_response(
            response,
            kind=TransactionKind.CAPTURE,
            success=response.status == TransactionStates.APPROVED,
        )
    except Exception as exc:
        return _error_response(TransactionKind.CAPTURE, exc, payment_information)


def refund(payment_information: PaymentData, config: GatewayConfig) -> GatewayResponse:
    kind = TransactionKind.REFUND
    payment_method = extract_payment_method(payment_information)
    payment_type = payment_method.get("type")
    if WOMPI_PAYMENT_METHODS.is_refund_available_for(payment_type):
        # process Payment
        # TODO: Add Code if we Wompi Starts supporting the Refund for any PaymnetType.
        # Currently, it doesnot support any refund.
        pass
    else:
        return _error_response(
            TransactionKind.REFUND,
            Exception(f"Refund Not supported by WOMPI for type: {payment_type}"),
            payment_information,
        )


def void(payment_information: PaymentData, config: GatewayConfig) -> GatewayResponse:
    payment_method = extract_payment_method(payment_information)
    kind = TransactionKind.VOID
    payment_type = payment_method.get("type")
    if WOMPI_PAYMENT_METHODS.is_void_available_for(payment_type):
        try:
            conf = config.connection_params
            tran_obj = TransactionRequest(conf)
            tra_id = payment_information.token
            gateway_resp = tran_obj.void(tra_id)
            response = _success_response(gateway_resp, kind=kind, success=True)
        except Exception as exc:
            response = _error_response(kind, exc, payment_information)
        return response
    else:
        return _error_response(
            TransactionKind.VOID,
            Exception(f"Void Not supported by WOMPI for type: {payment_type}"),
            payment_information,
        )


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
        error=str(exc),
        kind=kind,
        raw_response={},
        customer_id=payment_info.customer_id,
    )


def _success_response(
    intent,
    kind: str,  # use TransactionKind class
    success: bool = True,
    customer_id=None,
    raw_response=None,
):
    return GatewayResponse(
        is_success=success,
        action_required=intent.status == TransactionStates.PENDING,
        transaction_id=intent.id,
        amount=get_amount_from_wompi(intent.amount_in_cents),
        currency=intent.currency,
        error=None,
        kind=kind,
        raw_response=raw_response or intent,
        customer_id=customer_id,
    )
