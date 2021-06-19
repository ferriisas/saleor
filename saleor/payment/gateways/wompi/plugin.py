from typing import TYPE_CHECKING, List

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

# from . import GatewayConfig

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
        "Use sandbox": {
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": "Determines if Saleor should use Wompi sandbox API.",
            "label": "Use sandbox",
        },
        # "Store customers card": {
        #     "type": ConfigurationTypeField.BOOLEAN,
        #     "help_text": "Determines if Saleor should store cards on payments "
        #                  "in Wompi customer.",
        #     "label": "Store customers card",
        # },
        # "Automatic payment capture": {
        #     "type": ConfigurationTypeField.BOOLEAN,
        #     "help_text": "Determines if Saleor should automaticaly capture payments.",
        #     "label": "Automatic payment capture",
        # },
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
        {"name": "Public API key", "value": None},
        {"name": "Secret API key", "value": None},
        {"name": "Use sandbox", "value": True},
        {"name": "Store customers card", "value": False},
        {"name": "Automatic payment capture", "value": True},
        {"name": "Supported currencies", "value": ""},
    ]
    DEFAULT_ACTIVE = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configuration = {item["name"]: item["value"] for item in self.configuration}
        self.config = GatewayConfig(
            gateway_name=GATEWAY_NAME,
            auto_capture=True,  #  configuration["Automatic payment capture"],
            supported_currencies=configuration["Supported currencies"],
            connection_params={
                "sandbox_mode": configuration["Use sandbox"],
                "public_key": configuration["Public API key"],
                "private_key": configuration["Secret API key"],
            },
            store_customer=False,  # configuration["Store customers card"],
        )

    def _get_gateway_config(self):
        return self.config

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
        return get_client_token(self._get_gateway_config(), token_config)

    @require_active_plugin
    def get_supported_currencies(self, previous_value):
        config = self._get_gateway_config()
        return get_supported_currencies(config, GATEWAY_NAME)

    @require_active_plugin
    def get_payment_config(self, previous_value):
        config = self._get_gateway_config()
        return [
            {"field": "api_key", "value": config.connection_params["public_key"]},
            {"field": "store_customer_card", "value": config.store_customer},
        ]
