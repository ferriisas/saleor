from typing import TYPE_CHECKING, List

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseNotFound

from saleor.plugins.base_plugin import BasePlugin, ConfigurationTypeField

from ..utils import get_supported_currencies
from . import (
    GatewayConfig,
    authorize,
    capture,
    get_client_token,
    process_payment,
    refund,
    void,
)
from .webhooks import generate_acceptance_token, handle_webhook

WEBHOOK_PATH = "/webhooks"
GENERATE_ACP_TOKEN_PATH = "/acceptance-token"
GATEWAY_NAME = "Wompi"

if TYPE_CHECKING:
    # flake8: noqa
    from . import GatewayResponse, PaymentData
    from ...interface import CustomerSource


def require_active_plugin(fn):
    def wrapped(self, *args, **kwargs):
        previous = kwargs.get("previous_value", None)
        if not self.active:
            return previous
        return fn(self, *args, **kwargs)

    return wrapped


class WompiGatewayPlugin(BasePlugin):
    PLUGIN_NAME = GATEWAY_NAME
    PLUGIN_ID = "ferrii.payments.wompi"
    PLUGIN_DESCRIPTION = (
        "Wompi gateway, allow user make payments with credit cards, "
        "PSE and Bancolombia platforms like Nequi."
    )
    CONFIG_STRUCTURE = {
        "Sandbox Public API key": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Provide Wompi sandbox public API key.",
            "label": "Sandbox Public API key",
        },
        "Sandbox Secret API key": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Provide Wompi sandbox secret API key.",
            "label": "Sandbox Secret API key",
        },
        "Sandbox Event API key": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Provide Wompi sandbox event API key.",
            "label": "Sandbox Event API key",
        },
        "Public API key": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Provide Wompi public API key.",
            "label": "Public API key",
        },
        "Secret API key": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Provide Wompi secret API key.",
            "label": "Secret API key",
        },
        "Event API key": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "Provide Wompi event API key.",
            "label": "Event API key",
        },
        "Use sandbox": {
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": "Determines if Saleor should use Wompi sandbox API.",
            "label": "Use sandbox",
        },
        "Supported currencies": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Determines currencies supported by gateway."
            " Please enter currency codes separated by a comma.",
            "label": "Supported currencies",
        },
    }
    DEFAULT_CONFIGURATION = [
        {"name": "Sandbox Public API key", "value": None},
        {"name": "Sandbox Secret API key", "value": None},
        {"name": "Sandbox Event API key", "value": None},
        {"name": "Public API key", "value": None},
        {"name": "Secret API key", "value": None},
        {"name": "Event API key", "value": None},
        {"name": "Use sandbox", "value": True},
        {"name": "Store customers card", "value": False},
        {"name": "Automatic payment capture", "value": True},
        {"name": "Supported currencies", "value": ""},
    ]
    DEFAULT_ACTIVE = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configuration = {item["name"]: item["value"] for item in self.configuration}
        self.configuration_dict = configuration
        self.sandbox_mode = kwargs.get("sandbox_mode") or configuration.get(
            "Use sandbox", True
        )
        self.config = self.get_gateway_config()

    @property
    def _get_public_key(self):
        _ = "Sandbox Public API key" if self.sandbox_mode else "Public API key"
        return self.configuration_dict.get(_)

    @property
    def _get_private_key(self):
        _ = "Sandbox Secret API key" if self.sandbox_mode else "Secret API key"
        return self.configuration_dict.get(_)

    @property
    def _get_event_key(self):
        _ = "Sandbox Event API key" if self.sandbox_mode else "Event API key"
        return self.configuration_dict.get(_)

    def _get_gateway_config(self) -> GatewayConfig:
        return self.get_gateway_config()

    def get_gateway_config(self):
        return GatewayConfig(
            gateway_name=GATEWAY_NAME,
            auto_capture=True,
            supported_currencies=self.configuration_dict["Supported currencies"],
            connection_params={
                "sandbox_mode": self.sandbox_mode,
                "public_key": self._get_public_key,
                "private_key": self._get_private_key,
                "event_key": self._get_event_key,
            },
            store_customer=False,
        )

    def webhook(self, request: WSGIRequest, path: str, previous_value) -> HttpResponse:
        if path.startswith(WEBHOOK_PATH):
            return handle_webhook(request, self)
        elif path.startswith(GENERATE_ACP_TOKEN_PATH):
            return generate_acceptance_token(request, self)
        return HttpResponseNotFound()

    @require_active_plugin
    def authorize_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return authorize(payment_information, self._get_gateway_config())

    @require_active_plugin
    def capture_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return capture(payment_information, self._get_gateway_config())

    @require_active_plugin
    def refund_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return refund(payment_information, self._get_gateway_config())

    @require_active_plugin
    def void_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return void(payment_information, self._get_gateway_config())

    @require_active_plugin
    def process_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return process_payment(payment_information, self._get_gateway_config())

    # @require_active_plugin
    # def list_payment_sources(
    #         self, customer_id: str, previous_value
    # ) -> List["CustomerSource"]:
    #     sources = list_client_sources(self._get_gateway_config(), customer_id)
    #     previous_value.extend(sources)
    #     return previous_value

    @require_active_plugin
    def get_client_token(self, token_config: "TokenConfig", previous_value):
        return get_client_token(self.get_gateway_config(), token_config)

    @require_active_plugin
    def get_supported_currencies(self, previous_value):
        config = self.get_gateway_config()
        return get_supported_currencies(config, GATEWAY_NAME)

    @require_active_plugin
    def get_payment_config(self, previous_value):
        config = self.get_gateway_config()
        return [
            {"field": "api_key", "value": config.connection_params["public_key"]},
            {"field": "store_customer_card", "value": config.store_customer},
        ]
