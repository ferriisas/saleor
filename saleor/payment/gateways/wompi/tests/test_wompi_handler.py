from math import isclose
from unittest import mock

import pytest

from ....interface import AddressData
from ....utils import create_payment_information
from .. import TransactionKind, authorize, capture, get_client_token, refund, void
from ..client.wompi_handler import *
from .common import *


@pytest.mark.integration
def test_acceptance_token(sandbox_gateway_config):
    with mock.patch(
        "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
    ) as mock_acceptance_token:
        expected_response = read_json("acceptance_token.json")
        mock_acceptance_token.return_value = expected_response
        obj = AcceptanceTokenRequest(sandbox_gateway_config.connection_params)
        token = obj.send_request()
        assert (
            expected_response["data"]["presigned_acceptance"]["acceptance_token"]
            == token.acceptance_token
        )


@pytest.mark.integration
def test_tokenize_card(sandbox_gateway_config):
    with mock.patch(
        "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
    ) as mock_tokenize_card:
        payload = {
            "number": "4242424242424242",
            "cvc": "123",
            "exp_month": "08",
            "exp_year": "28",
            "card_holder": "José Pérez",
        }
        expected_resp = read_json("tokenize_card.json")
        mock_tokenize_card.return_value = expected_resp
        obj = TokenizeCardRequest(sandbox_gateway_config.connection_params)
        token = obj.tokenize_card(payload)
        assert f"Bearer {sandbox_gateway_config.connection_params['public_key']}" == obj._append_authorization(
            {}
        ).get(
            "Authorization"
        )
        assert expected_resp["data"]["id"] == token.id
        assert expected_resp["data"]["brand"] == token.brand
        assert expected_resp["data"]["card_holder"] == token.card_holder


@pytest.mark.integration
def test_get_financial_inst(sandbox_gateway_config):
    with mock.patch(
        "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
    ) as mock_fin_ins:
        expected_resp = read_json("financial_institution.json")
        mock_fin_ins.return_value = expected_resp
        obj = FinancialInstitutionsRequest(sandbox_gateway_config.connection_params)
        response = obj.send_request()

        assert f"Bearer {sandbox_gateway_config.connection_params['public_key']}" == obj._append_authorization(
            {}
        ).get(
            "Authorization"
        )
        assert len(expected_resp["data"]) == len(response)

        assert (
            expected_resp["data"][0]["financial_institution_code"]
            == response[0].financial_institution_code
        )
        assert (
            expected_resp["data"][0]["financial_institution_name"]
            == response[0].financial_institution_name
        )


@pytest.mark.integration
@pytest.mark.parametrize("payment_method", VARIOUS_METHODS)
def test_generate_transaction_success(payment_method, sandbox_gateway_config):
    with mock.patch(
        "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
    ) as mock_transaction:
        expected_resp = read_json("transaction.json")
        mock_transaction.return_value = expected_resp
        payload = {
            "acceptance_token": "random_123",
            "amount_in_cents": 2500000,
            "currency": "COP",
            "customer_email": "pepito_perez@example.com",
            "reference": "22234ed4",
            "payment_method": payment_method,
        }
        obj = TransactionRequest(sandbox_gateway_config.connection_params)
        response = obj.generate(payload)
        assert f"Bearer {sandbox_gateway_config.connection_params['private_key']}" == obj._append_authorization(
            {}
        ).get(
            "Authorization"
        )
        assert TransactionDAO(**expected_resp["data"]) == response


@pytest.mark.integration
@pytest.mark.parametrize("payment_method", VARIOUS_METHODS)
def test_generate_transaction_throws_validation_on_incomplete_data(
    payment_method, sandbox_gateway_config
):
    with mock.patch(
        "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
    ) as mock_transaction:
        payload = {
            "acceptance_token": "random_123",
            "amount_in_cents": 2500000,
            "currency": "COP",
            "customer_email": "pepito_perez@example.com",
            "reference": "22234ed4",
            "payment_method": payment_method,
        }

        with pytest.raises(TransactionRequest.exception_class) as execinfo:
            incomplete_payment_data = payload.copy()
            missing_key_name = "acceptance_token"
            del incomplete_payment_data[missing_key_name]
            obj = TransactionRequest(sandbox_gateway_config.connection_params)
            obj.generate(incomplete_payment_data)
        assert (
            missing_key_name in execinfo.value.args[0]
        ), f"{missing_key_name} not found in exception info."


@pytest.mark.integration
def test_get_transaction(sandbox_gateway_config):
    with mock.patch(
        "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
    ) as mock_transaction:
        expected_resp = read_json("transaction.json")
        mock_transaction.return_value = expected_resp
        obj = TransactionRequest(sandbox_gateway_config.connection_params)
        response = obj.retrieve(expected_resp["data"]["id"])
        assert TransactionDAO(**expected_resp["data"]) == response


@pytest.mark.integration
def test_void_transaction(sandbox_gateway_config):
    with mock.patch(
        "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
    ) as mock_transaction:
        # TODO: Add the correct response after checking from Wompi.
        expected_resp = read_json("transaction.json")
        mock_transaction.return_value = expected_resp
        obj = TransactionRequest(sandbox_gateway_config.connection_params)
        response = obj.void(expected_resp["data"]["id"])
        assert f"Bearer {sandbox_gateway_config.connection_params['private_key']}" == obj._append_authorization(
            {}
        ).get(
            "Authorization"
        )
        assert TransactionDAO(**expected_resp["data"]) == response


@pytest.mark.integration
@pytest.mark.parametrize("payment_method", VARIOUS_METHODS)
def test_refund_transaction(payment_method, sandbox_gateway_config):
    with pytest.raises(WompiNotImplementedException):
        # Wompi Doesn't support refund..So Will always get WompiNotImplementedException
        resp = read_json("transaction.json")
        obj = TransactionRequest(sandbox_gateway_config.connection_params)
        obj.refund(resp["data"]["id"])


@pytest.mark.integration
@pytest.mark.parametrize("payment_method", VARIOUS_METHODS)
def test_authorize(
    payment_method, sandbox_gateway_config, wompi_payment, address, acceptance_token
):
    with mock.patch(
        "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
    ) as mock_create_transaction:
        expected_resp = read_json("transaction.json")
        expected_resp["data"]["amount_in_cents"] = TRANSACTION_AMOUNT * 100
        mock_create_transaction.return_value = expected_resp
        payment_info = create_payment_information(
            wompi_payment,
            "test",
            additional_data={
                "acceptance_token": acceptance_token,
                "payment_method": payment_method,
            },
        )
        payment_info.shipping = AddressData(**address.as_data())
        response = authorize(payment_info, sandbox_gateway_config)
        assert response.is_success is True
        assert response.kind == TransactionKind.CAPTURE
        assert isclose(response.amount, TRANSACTION_AMOUNT)
        assert response.currency == TRANSACTION_CURRENCY
