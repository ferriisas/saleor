import json
from typing import Dict

import requests

from .constants import *
from .constants import WOMPI_PAYMENT_METHODS
from .objects import *


class WompiHandler:
    method_type = None
    authentication_required = False
    url = ""
    path = ""
    payload = ""
    exception_class = WompiUnknownException

    def __init__(self, config):
        self._key = config.get("public_key")
        self._secret = config.get("private_key")
        self.sandbox = config.get("sandbox", True)
        self.authentication_required = True
        assert self._key != None, "Invalid key for Wompi"
        assert self._secret != None, "Invalid Secret for Wompi"

    @property
    def _get_host(self):
        return WompiURL.SANDBOX_URL if self.sandbox else WompiURL.PRODUCTION_URL

    def _make_url(self, method_name):
        return "{}/{}".format(self._get_host, method_name)

    @property
    def _get_url(self):
        return self._make_url(self.path)

    def _append_authorization(self, headers):
        if self.authentication_required:
            headers["Authorization"] = "Bearer {}".format(self._secret)
        else:
            if "Authorization" in headers:
                del headers["Authorization"]

        return headers

    def send_request(self, **kwargs):
        headers = {"Content-Type": "application/json"}
        headers = self._append_authorization(headers)
        session = requests.Session()
        response = getattr(session, self.method_type)(
            self._get_url, headers=headers, data=kwargs.get("payload")
        )
        if response.status_code in HTTP_STATUS_CODE.OK_CODES:
            session.close()
            return response.json()
        else:
            raise HTTP_STATUS_EXCEPTION_MAPPING.get(
                response.status_code, WompiUnknownException
            )(response.text)


class TokenizeCardRequest(WompiHandler):
    path = "tokens/cards"
    method_type = MethodType.POST
    authentication_required = True
    DAO = CardInfoDAO

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _append_authorization(self, headers):
        # For Card TOkenization, we need to authenticate with public key.
        if self.authentication_required:
            headers["Authorization"] = "Bearer {}".format(self._key)
        return headers

    def tokenize_card(self, payload):
        required_keys = ["number", "cvc", "exp_month", "exp_year", "card_holder"]
        if not set(required_keys).issubset(set(payload.keys())):
            raise self.exception_class(
                "Required keys are not provided for card Tokenization"
            )

        self.payload = json.dumps(payload)
        return self.send_request(payload=self.payload)

    def send_request(self, **kwargs):
        resp = super().send_request(**kwargs)
        return self.DAO(**resp.get("data"))


class FinancialInstitutionsRequest(WompiHandler):
    path = "pse/financial_institutions"
    method_type = MethodType.GET
    authentication_required = True
    DAO = FinInstDAO

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _append_authorization(self, headers):
        # For Card TOkenization, we need to authenticate with public key.
        if self.authentication_required:
            headers["Authorization"] = "Bearer {}".format(self._key)
        return headers

    def send_request(self):
        resp = super().send_request()
        return [self.DAO(**row) for row in resp.get("data")]


class AcceptanceTokenRequest(WompiHandler):
    path = "merchants/{key}"
    method_type = MethodType.GET
    authentication_required = False
    DAO = AcceptanceTokenDAO

    @property
    def _get_url(self):
        return self._make_url(self.path.format(key=self._key))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_request(self):
        resp = super().send_request()
        return self.DAO(**resp.get("data"))


class TransactionRequest(WompiHandler):
    path = "transactions"
    method_type = MethodType.POST
    authentication_required = True
    DAO = TransactionDAO
    exception_class = WompiTransactionException
    required_transactin_keys = [
        "acceptance_token",
        "amount_in_cents",
        "customer_email",
        "reference",
        "payment_method",
    ]

    @property
    def _get_url(self):
        return self._make_url(self.path)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate_transaction_data(self, payload):
        required_keys = self.required_transactin_keys
        if not set(required_keys).issubset(set(payload.keys())):
            missing_key = set(required_keys) - set(payload.keys())
            raise self.exception_class(
                f"Required keys are not provided: {', '.join(missing_key)}"
            )
        WOMPI_PAYMENT_METHODS.is_valid_payment_data(payload.get("payment_method"))

    def generate(self, payload: Dict) -> TransactionDAO:
        self.method_type = MethodType.POST
        self.validate_transaction_data(payload)
        self.payload = json.dumps(payload)
        return self.send_request(payload=self.payload)

    def void(self, payment_id) -> TransactionDAO:
        self.path = "transactions/{}/void".format(payment_id)
        self.method_type = MethodType.POST
        self.authentication_required = True
        resp = super().send_request()
        return self.DAO(**resp.get("data", {}).get("transaction", {}))

    def refund(self, payment_id):
        # Implement the function when its available.
        raise WompiNotImplementedException("Refund Not supported by Wompi.")

    def retrieve(self, payment_id) -> TransactionDAO:
        self.path = "transactions/{}".format(payment_id)
        self.method_type = MethodType.GET
        self.authentication_required = False
        resp = super().send_request()
        return self.DAO(**resp.get("data"))

    def send_request(self, **kwargs) -> TransactionDAO:
        resp = super().send_request(**kwargs)
        return self.DAO(**resp.get("data"))
