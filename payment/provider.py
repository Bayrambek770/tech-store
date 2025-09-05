import base64
import urllib

from django.conf import settings

from .models import Transaction, TransactionStatus


class InterforumClient:
    ORDER_NOT_FOUND = "303"
    ORDER_ALREADY_PAID = "201"
    INVALID_AMOUNT = "5"
    SERVER_ERROR = "3"
    SUCCESS = "0"

    SUCCESS_STATUS_TEXT = "OK"
    ERROR_STATUS_TEXT = "ERROR"

    def __init__(self, params: dict = None):
        # for merchant
        self.params = params
        self.code = self.SUCCESS
        self.error = False
        self.transaction = self.get_transaction()

    def get_transaction(self):
        if not self.params or not self.params.get("account"):
            return
        try:
            return Transaction.objects.get(id=self.params["account"]["order_id"])
        except Transaction.DoesNotExist:
            return

    @classmethod
    def create_payment_link(cls, transaction):
        amount = transaction.amount
        currency_code = transaction.currency
        return_url = "https://darkandwhite.uz/"
        if currency_code == "UZS":
            currency = 860
        elif currency_code == "USD":
            currency = 840
        query_params = {
            "merchant_id": settings.PAYLOV_MERCHANT_ID,
            "amount": amount,
            "currency_id": currency,
            "amount_in_tiyin": True,
            "return_url": return_url,
            "account.order_id": transaction.id,
        }
        query = urllib.parse.urlencode(query_params)
        encode_params = base64.b64encode(query.encode("utf-8"))
        encode_params = str(encode_params, "utf-8")
        base_link = "https://my.paylov.uz/checkout/create"
        url = f"{base_link}/{encode_params}"
        transaction.payment_url=url
        transaction.save()
        return url

    def check_transaction(self):
        if not self.transaction:
            return True, self.ORDER_NOT_FOUND

        self.validate_transaction()
        self.validate_amount(self.params["amount_tiyin"])

        return self.error, self.code

    def perform_transaction(self):
        if not self.transaction:
            return True, self.ORDER_NOT_FOUND

        if self.transaction.status == TransactionStatus.FAILED:
            return True, self.SERVER_ERROR

        self.validate_transaction()
        self.validate_amount(self.params["amount_tiyin"])

        return self.error, self.code

    def validate_transaction(self):
        if self.transaction.status == TransactionStatus.SUCCESS:
            self.error = True
            self.code = self.ORDER_ALREADY_PAID

    def validate_amount(self, amount):
        transaction_amount = int(self.transaction.amount)
        if amount != transaction_amount:
            self.error = True
            self.code = self.INVALID_AMOUNT
