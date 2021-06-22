from .error_code import ERROR_CODE
from .http_status_code import HTTP_STATUS_CODE
from .url import WompiURL


class MethodType:
    GET = "get"
    POST = "post"


class TransactionStates:
    # Valid Wompi Transaction States.
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    VOIDED = "VOIDED"
    ERROR = "ERROR"


class WOMPI_PAYMENT_METHODS:
    CARD = "CARD"
    NEQUI = "NEQUI"
    PSE = "CARD"
    CASH_AT_BBC = "CARD"
    BANC_TRA_Button = "BANCOLOMBIA_COLLECT"


class WebhookEvents:
    TXN_UPDATE = "transaction.updated"
    NEQI_UPDATE = "nequi_token.updated	"


__all__ = [
    "HTTP_STATUS_CODE",
    "ERROR_CODE",
    "WompiURL",
    "MethodType",
    "TransactionStates",
    "WOMPI_PAYMENT_METHODS",
    "WebhookEvents",
]
