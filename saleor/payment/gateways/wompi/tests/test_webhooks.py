import json
from unittest import mock

import pytest

from ..client.constants import TransactionStates
from ..webhooks import generate_acceptance_token, generate_checksum, handle_webhook
from .common import *


def test_checksum(wompi_plugin):
    plugin = wompi_plugin(is_sandbox=True, api_event="test123")
    expected_value = "125d467a792c701c59c7967e7207624c9fa563e68a302c85eb642a4ebab85890"
    request_data = read_json("transaction_webhook.json")
    request_data["data"]["transaction"]["id"] = "testId"
    request_data["data"]["transaction"]["status"] = "APPROVED"
    request_data["data"]["transaction"]["amount_in_cents"] = "454500"
    request_data["data"]["timestamp"] = 1530291411

    generated_checksum = generate_checksum(request_data, plugin.get_gateway_config())
    assert expected_value == generated_checksum


@mock.patch(
    "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
)
def test_generate_acceptance_token(mock_request, wompi_plugin):
    expected_resp = read_json("acceptance_token.json")
    mock_request.return_value = expected_resp
    request_mock = mock.Mock()
    request_mock.GET = {}
    response = generate_acceptance_token(request_mock, wompi_plugin())

    response_data = json.loads(response.content)
    assert (
        response_data["acceptance_token"]
        == expected_resp["data"]["presigned_acceptance"]["acceptance_token"]
    )
    assert (
        response_data["permalink"]
        == expected_resp["data"]["presigned_acceptance"]["permalink"]
    )
    assert response.status_code == 200


@mock.patch("saleor.payment.gateways.wompi.client.wompi_handler.requests.Session.get")
def test_generate_acceptance_token_return_error(mock_request, wompi_plugin):
    exception_text = "Raised Dummy Exception"
    mock_request.return_value.url = ""
    mock_request.return_value.status_code = 400
    mock_request.return_value.text = exception_text
    request_mock = mock.Mock()
    request_mock.GET = {}
    response = generate_acceptance_token(request_mock, wompi_plugin())
    assert 400 == response.status_code
    assert exception_text in str(response.content)


def test_handle_webhook_validate_checksum(wompi_plugin):
    request_data = read_json("transaction_webhook.json")
    request_mock = mock.Mock()
    request_mock.GET = {}
    request_mock.GET = {}
    request_mock.POST = json.dumps(request_data)
    request_mock.body = json.dumps(request_data)

    with mock.patch(
        "saleor.payment.gateways.wompi.webhooks.generate_checksum"
    ) as mock_checksum:
        mock_checksum.return_value = request_data.get("signature", {}).get("checksum")
        response = handle_webhook(request_mock, wompi_plugin())
        assert response.status_code == 200
        mock_checksum.return_value = None
        response = handle_webhook(request_mock, wompi_plugin())
        assert response.status_code == 400
        assert response.content == b"Invalid Checksum."


@pytest.mark.parametrize(
    "txn_status,process_order",
    [
        (
            TransactionStates.PENDING,
            False,
        ),  # DOne't process order..It may be just for acknowledgement.
        (TransactionStates.APPROVED, True),  # Capture the pyment and procss the Order.
        (TransactionStates.VOIDED, False),  #  Txn Cancelled. DOn't prpcess the order.
        (
            TransactionStates.DECLINED,
            False,
        ),  # Txn declined. o=Don't process the oprder.
    ],
)
def test_handle_webhook(txn_status, process_order, wompi_plugin):
    request_data = read_json("transaction_webhook.json")
    request_data["data"]["transaction"]["status"] = txn_status
    request_mock = mock.Mock()
    request_mock.GET = {}
    request_mock.GET = {}
    request_mock.POST = json.dumps(request_data)
    request_mock.body = json.dumps(request_data)

    with mock.patch(
        "saleor.payment.gateways.wompi.webhooks.generate_checksum"
    ) as mock_checksum:
        mock_checksum.return_value = request_data.get("signature", {}).get("checksum")
        response = handle_webhook(request_mock, wompi_plugin())
        assert response.status_code == 200
