import json

MOCK_RESPONSE_PATH = "saleor/payment/gateways/wompi/client/mock_responses"


def _get_file_path(file_name):
    return "{}/{}".format(MOCK_RESPONSE_PATH, file_name)


def read_json(file_name):
    with open(_get_file_path(file_name)) as f:
        return json.load(f)
