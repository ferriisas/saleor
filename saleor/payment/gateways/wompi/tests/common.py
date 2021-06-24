import json

MOCK_RESPONSE_PATH = "saleor/payment/gateways/wompi/client/mock_responses"


def _get_file_path(file_name):
    return "{}/{}".format(MOCK_RESPONSE_PATH, file_name)


def read_json(file_name):
    with open(_get_file_path(file_name)) as f:
        return json.load(f)


CC_PAYMENT_METHOD = {
    "type": "CARD",
    "token": "tok_prod_1_BBb749EAB32e97a2D058Dd538a608301",
}

BCOL_PAYMENT_METHOD = {
    "type": "BANCOLOMBIA_TRANSFER",
    "user_type": "PERSON",
    "payment_description": "Pago a Tienda Wompi",
    "sandbox_status": "APPROVED",
}
NEQI_PAYMENT_METHOD = {
    "type": "NEQUI",
    "phone_number": "3991111111"  # Success
    # "phone_number": "3992222222" # Error
}
FIN_INST_PAYMENT_METHOD = {
    "type": "PSE",
    "user_type": 0,
    "user_legal_id_type": "CC",
    "user_legal_id": "1099888777",
    "financial_institution_code": "1",
    "payment_description": "Pago a Tienda Wompi, ref: JD38USJW2XPLQA",
}
CASH_PAYMENT_METHOD = {"type": "BANCOLOMBIA_COLLECT"}
VARIOUS_METHODS = [
    CC_PAYMENT_METHOD,
    BCOL_PAYMENT_METHOD,
    NEQI_PAYMENT_METHOD,
    FIN_INST_PAYMENT_METHOD,
    CASH_PAYMENT_METHOD,
]
PAYMENT_DATA = {"acceptance_token": "", "payment_method": "VARIOUS_METHODS"}
#
# PAYMENT_DATA = {
#     "acceptance_token": "",
#     "amount": 2500000,
#     "currency": "COP",
#     "customer_email": "pepito_perez@example.com",
#     "reference": "2322er3234ed4",
#     "payment_method": VARIOUS_METHODS[0],
# }
