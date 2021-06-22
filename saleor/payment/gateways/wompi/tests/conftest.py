from unittest import mock

import pytest

from .....plugins.manager import get_plugins_manager
from ..plugin import WompiGatewayPlugin


@pytest.fixture
def wompi_plugin(settings):
    def fun(api_key=None, api_secret=None, api_event=None, is_sandbox=True):
        api_key = api_key or "test_key"
        api_secret = api_secret or "test_secret"
        settings.PLUGINS = ["saleor.payment.gateways.wompi.plugin.WompiGatewayPlugin"]
        manager = get_plugins_manager()

        with mock.patch(
            "saleor.payment.gateways.wompi.client.wompi_handler.WompiHandler.send_request"
        ):
            manager.save_plugin_configuration(
                WompiGatewayPlugin.PLUGIN_ID,
                {
                    "active": True,
                    "configuration": [
                        {"name": "Sandbox Public API key", "value": api_key},
                        {"name": "Sandbox Secret API key", "value": api_secret},
                        {"name": "Sandbox Event API key", "value": api_event},
                        {"name": "Public API key", "value": api_key},
                        {"name": "Secret API key", "value": api_secret},
                        {"name": "Event API key", "value": api_event},
                        {"name": "Use sandbox", "value": is_sandbox},
                        {"name": "Store customers card", "value": False},
                        {"name": "Automatic payment capture", "value": True},
                        {"name": "Supported currencies", "value": False},
                    ],
                },
            )

        manager = get_plugins_manager()
        return manager.plugins[0]

    return fun
