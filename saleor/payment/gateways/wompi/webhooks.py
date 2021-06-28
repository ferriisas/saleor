import base64
import binascii
import hashlib
import json
import logging
from json.decoder import JSONDecodeError
from typing import Any, Callable, Dict, Optional

from django.core.handlers.wsgi import WSGIRequest
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    JsonResponse,
    QueryDict,
)
from django.http.request import HttpHeaders
from graphql_relay import from_global_id

from ....core.transactions import transaction_with_commit_on_errors
from ....payment.models import Payment, Transaction
from . import GatewayConfig
from .client.constants import WebhookEvents
from .client.objects import TransactionDAO
from .client.wompi_handler import AcceptanceTokenRequest

logger = logging.getLogger(__name__)


def generate_checksum(data, config: GatewayConfig):
    txn = data.get("data", {}).get("transaction", {})
    checksum_str = "{}-{}-{}{}{}".format(
        txn.get("id"),
        txn.get("status"),
        txn.get("amount_in_cents"),
        data.get("timestamp"),
        config.connection_params.get("event_key"),
    )
    return hashlib.sha256(checksum_str.encode("utf-8")).hexdigest()


def get_payment(transaction_id,) -> Optional[Payment]:
    payments = (
        Payment.objects.prefetch_related("order", "checkout")
        .select_for_update(of=("self",))
        .filter(token=transaction_id, gateway="ferrii.payments.wompi")
    )
    payment = payments.first()
    if not payment:
        logger.warning(
            "Payment for Transaction was not found. Reference %s", transaction_id,
        )
    return payment


def generate_acceptance_token(request: WSGIRequest, plugin):
    logger.info("Webhook request for WOMPI for generating Acceptance Token. %s")
    config = plugin.get_gateway_config().connection_params
    wh = AcceptanceTokenRequest(config)
    token = wh.send_request()
    return JsonResponse(token.__dict__)


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

    if event == WebhookEvents.TXN_UPDATE:
        txn_data = json_data.get("data", {}).get("transaction", {})
        transaction_id = TransactionDAO(**txn_data)

        # plugin.capture()
    # event_handler = EVENT_MAP.get(notification.get("eventCode", ""))
    # if event_handler:
    #     event_handler(notification, gateway_config)
    #     return HttpResponse("[accepted]")
    return HttpResponse("[accepted]")
