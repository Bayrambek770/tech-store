import requests
from django.db import transaction as db_transaction

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.auth import authentication as paylov_auth
from payment.provider import InterforumClient as PaylovProvider
from payment.utils import PaylovMethods

from .models import Transaction, TransactionStatus
from .serializers import PaylovSerializer


class PaylovAPIView(APIView):
    permission_classes = [AllowAny]
    http_method_names = ["post"]
    authentication_classes = []  # type: ignore

    def __init__(self):
        self.METHODS = {
            PaylovMethods.CHECK_TRANSACTION: self.check,
            PaylovMethods.PERFORM_TRANSACTION: self.perform,
        }
        self.params = None
        super(APIView, self).__init__()

    def post(self, request, *args, **kwargs):
        check = paylov_auth(request)
        if check is False or not check:
            return Response(status=403)
        serializer = PaylovSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)

        method = serializer.validated_data["method"]
        self.params = serializer.validated_data["params"]

        with db_transaction.atomic():
            response_data = self.METHODS[method]()

        if isinstance(response_data, dict):
            response_data.update({"jsonrpc": "2.0", "id": request.data.get("id", None)})

        return Response(response_data)

    def check(self):
        error, code = PaylovProvider(self.params).check_transaction()
        if error:
            return dict(
                result=dict(status=code, statusText=PaylovProvider.ERROR_STATUS_TEXT)
            )

        return dict(
            result=dict(status=code, statusText=PaylovProvider.SUCCESS_STATUS_TEXT)
        )

    def perform(self):
        error, code = PaylovProvider(self.params).perform_transaction()

        # when order is not found
        if error and code == PaylovProvider.ORDER_NOT_FOUND:
            return dict(
                result=dict(status=code, statusText=PaylovProvider.ERROR_STATUS_TEXT)
            )

        transaction = Transaction.objects.get(id=self.params["account"]["order_id"])
        transaction_id = self.params["transaction_id"]
        # when order found and transaction created but error occurred
        if error:
            transaction.transaction_id = transaction_id
            transaction.status = TransactionStatus.FAILED
            transaction.save()
            return dict(
                result=dict(status=code, statusText=PaylovProvider.ERROR_STATUS_TEXT)
            )
        # if everything is ok
        transaction.process_after_succesful_payment(transaction_id)

        return dict(
            result=dict(status=code, statusText=PaylovProvider.SUCCESS_STATUS_TEXT)
        )
