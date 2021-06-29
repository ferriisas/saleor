from dataclasses import dataclass

from .constants import TransactionStates


@dataclass()
class FinInstDAO:
    financial_institution_code: str
    financial_institution_name: str


@dataclass(init=False)
class CardInfoDAO:
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
    amount_in_cents: str
    reference: str
    currency: str
    payment_method_type: str
    status: str
    payment_method: dict = None
    customer_email: str = None
    shipping_address: str = None
    payment_source_id: str = None
    payment_link_id: str = None
    customer_data: str = None
    bill_id: str = None
    created_at: str = None

    def __init__(self, **kwargs):
        for _ in kwargs:
            setattr(self, _, kwargs[_])

    @property
    def vendor_transaction_id(self):
        """
        Returns the Payment Transaction of Wompi.
        :return:
        """
        if self.payment_method:
            extra = self.payment_method.get("extra", {})
            return extra.get("transaction_id")

    @property
    def is_pending(self):
        return self.status == TransactionStates.PENDING

    @property
    def is_approved(self):
        return self.status == TransactionStates.APPROVED

    @property
    def is_declined(self):
        return self.status == TransactionStates.DECLINED

    @property
    def is_voided(self):
        return self.status == TransactionStates.VOIDED

    @property
    def is_error(self):
        return self.status == TransactionStates.ERROR
