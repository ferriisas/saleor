from decimal import Decimal
from unittest import mock

import pytest

from .... import TransactionKind
from ....utils import create_payment_information
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
        assert response.kind == TransactionKind.CAPTURE
        assert response.amount == Decimal("25000")
        assert response.error is None
        assert response.action_required_data is None


@pytest.mark.parametrize("payment_method_data", VARIOUS_METHODS)
def test_authorize_payment(
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


@pytest.mark.parametrize("payment_method_data", VARIOUS_METHODS)
def test_capture_payment(
    payment_method_data, payment_wompi_for_checkout, checkout_with_items, wompi_plugin
):
    with mock.patch(
        "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
    ) as mock_transaction:
        pass

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
        (CC_PAYMENT_METHOD, True),
        (BCOL_PAYMENT_METHOD, False),
        (NEQI_PAYMENT_METHOD, False),
        (FIN_INST_PAYMENT_METHOD, False),
        (CASH_PAYMENT_METHOD, False),
    ],
)
def test_void_payment(
    payment_method_data,
    available,
    payment_wompi_for_checkout,
    checkout_with_items,
    wompi_plugin,
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
def test_refund_payment(
    payment_method_data,
    available,
    payment_wompi_for_checkout,
    checkout_with_items,
    wompi_plugin,
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
        refund_payment = wompi_plugin.refund_payment(payment_info, None)
        assert refund_payment.is_success == available
