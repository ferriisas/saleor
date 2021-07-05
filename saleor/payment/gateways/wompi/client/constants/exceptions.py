from .http_status_code import *


class WompiTransactionException(Exception):
    pass


class WompiUnauthorizedException(Exception):
    pass


class WompiNotFoundException(Exception):
    pass


class WompiValidationException(Exception):
    pass


class WompiUnknownException(Exception):
    pass


class WompiNotImplementedException(Exception):
    pass


HTTP_STATUS_EXCEPTION_MAPPING = {
    HTTP_STATUS_CODE.Unauthorized: WompiUnauthorizedException,
    HTTP_STATUS_CODE.NotFound: WompiNotFoundException,
    HTTP_STATUS_CODE.ValidationError: WompiValidationException,
}
