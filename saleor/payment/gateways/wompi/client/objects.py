from dataclasses import dataclass


@dataclass(init=False)
class CardInfo:
    id: str
    created_at: str
    brand: str
    name: str
    last_four: str
    bin: str
    exp_year: str
    exp_month: str
    card_holder: str
    expires_at: str

    def __init__(self, **kwargs):
        for _ in kwargs:
            setattr(self, _, kwargs[_])


@dataclass(init=False)
class AcceptanceTokenDAO:
    acceptance_token: str
    permalink: str

    def __init__(self, **kwargs):
        presigned_acceptance = kwargs.get("presigned_acceptance", {})
        self.acceptance_token = presigned_acceptance.get("acceptance_token")
        self.permalink = presigned_acceptance.get("permalink")


@dataclass(init=False)
class TransactionDAO:
    id: str
    created_at: str
    amount_in_cents: str
    reference: str
    currency: str
    payment_method_type: str
    status: str
    payment_method: dict
    customer_email: str = None
    shipping_address: str = None
    payment_source_id: str = None
    payment_link_id: str = None
    customer_data: str = None
    bill_id: str = None

    def __init__(self, **kwargs):
        for _ in kwargs:
            setattr(self, _, kwargs[_])

    @property
    def vendor_transaction_id(self):
        """
        Returns the Payment Transaction Iof Wompi.
        :return:
        """
        if self.payment_method:
            extra = self.payment_method.get("extra", {})
            return extra.get("transaction_id")
