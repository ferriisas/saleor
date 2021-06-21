import json
from unittest import mock

import pytest

from ..webhooks import generate_checksum, handle_webhook

MOCK_RESPONSE_PATH = "saleor/payment/gateways/wompi/client/mock_responses"


def _get_file_path(file_name):
    return "{}/{}".format(MOCK_RESPONSE_PATH, file_name)


def read_json(file_name):
    with open(_get_file_path(file_name)) as f:
        return json.load(f)


def test_checksum(wompi_plugin):
    plugin = wompi_plugin(is_sandbox=True, api_secret="test123")
    expected_value = "125d467a792c701c59c7967e7207624c9fa563e68a302c85eb642a4ebab85890"
    request_data = read_json("transaction_webhook.json")
    request_data["data"]["transaction"]["id"] = "testId"
    request_data["data"]["transaction"]["status"] = "APPROVED"
    request_data["data"]["transaction"]["amount_in_cents"] = "454500"
    request_data["data"]["timestamp"] = 1530291411

    generated_checksum = generate_checksum(request_data, plugin.get_gateway_config())
    assert expected_value == generated_checksum


def test_handle_webhook(wompi_plugin):
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
