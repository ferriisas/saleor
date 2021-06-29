from math import isclose
from unittest import mock

import pytest

from ....interface import AddressData
from ....models import Payment
from ....utils import create_payment_information
from .. import TransactionKind, authorize, capture, get_client_token, refund, void
from ..client.constants import *
from .common import *


@pytest.mark.parametrize("payment_method_data", VARIOUS_METHODS)
def test_process_payment(
    payment_method_data, payment_wompi_for_checkout, checkout_with_items, wompi_plugin
):
    with mock.patch(
        "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
    ) as mock_transaction:
        expected_resp = read_json("transaction.json")
        mock_transaction.return_value = expected_resp
        payment_info = create_payment_information(
            payment_wompi_for_checkout,
            additional_data={
                "payment_method": payment_method_data,
                "acceptance_token": "test_token",
            },
        )
        wompi_plugin = wompi_plugin()
        response = wompi_plugin.process_payment(payment_info, None)
        assert response.is_success is True
        assert response.action_required is True
        assert response.kind == TransactionKind.AUTH
        assert response.amount == Decimal("25000")
        assert response.error is None
        assert response.action_required_data is None


@pytest.mark.integration
@pytest.mark.parametrize("payment_method", VARIOUS_METHODS)
def test_authorize(
    payment_method, sandbox_gateway_config, wompi_payment, address, acceptance_token
):
    with mock.patch(
        "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
    ) as mock_create_transaction:
        expected_resp = read_json("transaction.json")
        transaction_id = expected_resp["data"]["id"]
        wompi_payment.token = transaction_id
        wompi_payment.save()
        expected_resp["data"]["amount_in_cents"] = TRANSACTION_AMOUNT * 100
        mock_create_transaction.return_value = expected_resp
        payment_info = create_payment_information(
            wompi_payment,
            wompi_payment.token,
            additional_data={
                "acceptance_token": acceptance_token,
                "payment_method": payment_method,
            },
        )
        payment_info.shipping = AddressData(**address.as_data())
        response = authorize(payment_info, sandbox_gateway_config)
        assert response.is_success is True
        assert response.kind == TransactionKind.AUTH
        assert isclose(response.amount, TRANSACTION_AMOUNT)
        assert response.currency == TRANSACTION_CURRENCY


@pytest.mark.parametrize("payment_method_data", VARIOUS_METHODS)
def test_capture_payment(
    payment_method_data, payment_wompi_for_checkout, checkout_with_items, wompi_plugin
):
    with mock.patch(
        "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
    ) as mock_transaction:
        expected_resp = read_json("transaction.json")
        mock_transaction.return_value = expected_resp
        payment_info = create_payment_information(
            payment_wompi_for_checkout,
            additional_data={
                "payment_method": payment_method_data,
                "acceptance_token": "test_token",
            },
        )
        wompi_plugin = wompi_plugin()
        response = wompi_plugin.process_payment(payment_info, None)


@pytest.mark.parametrize(
    "payment_method_data, available",
    [
        (CC_PAYMENT_METHOD, True),  # TODO: Write this scenario.
        (BCOL_PAYMENT_METHOD, False),
        (NEQI_PAYMENT_METHOD, False),
        (FIN_INST_PAYMENT_METHOD, False),
        (CASH_PAYMENT_METHOD, False),
    ],
)
def test_void_payment(
    payment_method_data,
    available,
    payment_txn_captured,
    checkout_with_items,
    wompi_plugin,
):
    with mock.patch(
        "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
    ) as mock_void:
        expected_resp = read_json("void_txn.json")
        mock_void.return_value = expected_resp
        wompi_plugin = wompi_plugin()
        payment = payment_txn_captured
        payment.gateway = wompi_plugin.PLUGIN_ID
        payment_info = create_payment_information(
            payment,
            expected_resp["data"]["transaction"]["id"],
            additional_data={
                "payment_method": payment_method_data,
                "acceptance_token": "test_token",
            },
        )
        void_payment = wompi_plugin.void_payment(payment_info, None)
        assert void_payment.is_success == available


@pytest.mark.parametrize(
    "payment_method_data, available",
    [
        (CC_PAYMENT_METHOD, False),
        (BCOL_PAYMENT_METHOD, False),
        (NEQI_PAYMENT_METHOD, False),
        (FIN_INST_PAYMENT_METHOD, False),
        (CASH_PAYMENT_METHOD, False),
    ],
)
@mock.patch(
    "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
)
def test_refund_payment(
    mock_wompi, payment_method_data, available, payment_txn_captured, wompi_plugin,
):

    TRANSACTION_ID = "rjfqmf3r"
    payment_info = create_payment_information(
        payment_txn_captured,
        TRANSACTION_ID,
        additional_data={
            "payment_method": payment_method_data,
            "acceptance_token": "test_token",
        },
    )
    wompi_plugin = wompi_plugin()
    refund_payment = wompi_plugin.refund_payment(payment_info, None)

    # Since Refund not supported, so will always get refund_payment
    assert refund_payment.is_success == available
