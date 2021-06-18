import json

import requests

from .constants import WompiURL as URL


class Client:
    """Wompi client class"""

    DEFAULTS = {
        "base_url": URL.PRODUCTION_URL,
        "sandbox_url": URL.SANDBOX_URL,
    }

    def __init__(self, session=None, auth=None, sandbox=True, **options):
        """
        Initialize a Client object with session,
        optional auth handler, and options
        """

        self.session = session or requests.Session()
        self.auth = auth

        if sandbox:
            self.base_url = self._set_sandbox_url(**options)
        else:
            self.base_url = self._set_base_url(**options)

    def _set_base_url(self, **options):
        base_url = self.DEFAULTS["base_url"]

        if "base_url" in options:
            base_url = options["base_url"]
            del options["base_url"]

        return base_url

    def _set_sandbox_url(self, **options):
        sandbox_url = self.DEFAULTS["sandbox_url"]

        if "sandbox_url" in options:
            sandbox_url = options["sandbox_url"]
            del options["sandbox_url"]

        return sandbox_url

    def request(self, method, path, **options):
        """
        Dispatches a request to the Wompi HTTP API
        """

        url = f"{self.base_url}{path}"
        response = getattr(self.session, method)(url, auth=self.auth, **options)

    def get(self, path, params, **options):
        """
        Parses GET request options and dispatches a request
        """
        return self.request("get", path, params=params, **options)

    def post(self, path, data, **options):
        """
        Parses POST request options and dispatches a request
        """
        data, options = self._update_request(data, options)
        return self.request("post", path, data=data, **options)

    def patch(self, path, data, **options):
        """
        Parses PATCH request options and dispatches a request
        """
        data, options = self._update_request(data, options)
        return self.request("patch", path, data=data, **options)

    def delete(self, path, data, **options):
        """
        Parses DELETE request options and dispatches a request
        """
        data, options = self._update_request(data, options)
        return self.request("delete", path, data=data, **options)

    def put(self, path, data, **options):
        """
        Parses PUT request options and dispatches a request
        """
        data, options = self._update_request(data, options)
        return self.request("put", path, data=data, **options)

    def _update_request(self, data, options):
        """
        Updates The resource data and header options
        """

        data["userName"] = self.auth[0]
        data["password"] = self.auth[1]
        data["locale"] = "co"

        if "headers" not in options:
            options["headers"] = {}

        options["headers"].update({"Content-type": "application/x-www-form-urlencoded"})
        options["headers"].update({"Accept": "application/json"})

        return data, options
