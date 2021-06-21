import hashlib
import json
import logging
from json.decoder import JSONDecodeError

from django.core.handlers.wsgi import WSGIRequest
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    QueryDict,
)
from django.http.request import HttpHeaders

from ....core.transactions import transaction_with_commit_on_errors
from . import GatewayConfig
from .client.constants import WebhookEvents

logger = logging.getLogger(__name__)


def generate_checksum(data, config: GatewayConfig):
    txn = data.get("data", {}).get("transaction", {})
    checksum_str = "{}-{}-{}{}{}".format(
        txn.get("id"),
        txn.get("status"),
        txn.get("amount_in_cents"),
        data.get("timestamp"),
        config.connection_params.get("private_key"),
    )
    return hashlib.sha256(checksum_str.encode("utf-8")).hexdigest()


@transaction_with_commit_on_errors()
def handle_webhook(request: WSGIRequest, plugin):
    logger.info("Webhook request for WOMPI. %s", request.body)
    try:
        json_data = json.loads(request.body)
    except JSONDecodeError:
        logger.warning("Cannot parse request body.")
        return HttpResponse("[accepted]")
    event = json_data.get("event")
    checksum = json_data.get("signature", {}).get("checksum")
    plugin.sandbox_mode = json_data.get("environment") != "prod"
    if checksum != generate_checksum(json_data, plugin.get_gateway_config()):
        # Checksum is invalid.
        return HttpResponseBadRequest("Invalid Checksum.")

    # if not validate_merchant_account(notification, gateway_config):
    #     logger.warning("Not supported merchant account.")
    #     return HttpResponse("[accepted]")
    # if not validate_hmac_signature(notification, gateway_config):
    #     return HttpResponseBadRequest("Invalid or missing hmac signature.")
    # if not validate_auth_user(request.headers, gateway_config):
    #     return HttpResponseBadRequest("Invalid or missing basic auth.")
    #
    # event_handler = EVENT_MAP.get(notification.get("eventCode", ""))
    # if event_handler:
    #     event_handler(notification, gateway_config)
    #     return HttpResponse("[accepted]")
    return HttpResponse("[accepted]")
