from dataclasses import dataclass


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
    payment_method: dict
    status: str
    customer_email: str = None
    shipping_address: str = None
    payment_source_id: str = None
    payment_link_id: str = None
    customer_data: str = None
    bill_id: str = None

    def __init__(self, **kwargs):
        for _ in kwargs:
            setattr(self, _, kwargs[_])
