from .error_code import ERROR_CODE
from .exceptions import (
    HTTP_STATUS_EXCEPTION_MAPPING,
    WompiNotFoundException,
    WompiNotImplementedException,
    WompiTransactionException,
    WompiUnauthorizedException,
    WompiUnknownException,
    WompiValidationException,
)
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
    BANC_TRA_Button = "BANCOLOMBIA_TRANSFER"
    NEQUI = "NEQUI"
    PSE = "PSE"
    BANCOLOMBIA_COLLECT = "BANCOLOMBIA_COLLECT"

    # Option which define current active payment method for Wompi.
    ACTIVE_PAYMENTS = [CARD, BANC_TRA_Button, NEQUI, PSE, BANCOLOMBIA_COLLECT]

    # Refund  not Allowed for AnyPaymentMethod
    ALLOWED_TYPE_REFUND = []

    #
    ALLOWED_TYPE_VOID = [CARD]

    REQUIRED_FIELDS = {
        CARD: ["type", "token"],
        BANC_TRA_Button: ["type", "user_type", "payment_description"],
        NEQUI: ["type", "phone_number"],
        PSE: [
            "type",
            "user_type",
            "user_legal_id_type",
            "user_legal_id",
            "financial_institution_code",
            "payment_description",
        ],
        BANCOLOMBIA_COLLECT: ["type"],
    }

    # We will check the data inside 'extra' params inside payment_method after creating the transaction

    RESPONSE_FROM_WOMPI: {
        BANC_TRA_Button: ["async_payment_url"],
        PSE: ["async_payment_url"],
        BANCOLOMBIA_COLLECT: [
            "business_agreement_code",
            "payment_intention_identifier",
        ],
    }

    @classmethod
    def is_valid_payment_data(cls, payment_method_data):
        # Validates the Fields required for Different Payment Method
        type = payment_method_data.get("type")
        if type not in cls.ACTIVE_PAYMENTS:
            raise WompiValidationException(f"Payment type is {type} not active")

        keys = payment_method_data.keys()
        required_fields = cls.REQUIRED_FIELDS.get(type, {})
        if set(required_fields).issubset(set(keys)):
            return True
        else:
            missing_fields = set(required_fields) - set(keys)
            raise WompiValidationException(
                f"Missing fields for payment type {type}: "
                f"{',' .join(list(missing_fields))}"
            )

    @classmethod
    def is_refund_available_for(cls, payment_type):
        return payment_type in cls.ALLOWED_TYPE_REFUND

    @classmethod
    def is_void_available_for(cls, payment_type):
        return payment_type in cls.ALLOWED_TYPE_VOID


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
    ## Exceptions
    "WompiTransactionException",
    "WompiUnauthorizedException",
    "WompiNotFoundException",
    "WompiValidationException",
    "WompiUnknownException",
    "WompiNotImplementedException",
    "HTTP_STATUS_EXCEPTION_MAPPING",
]
