from django.db import models
from django.db import transaction as db_transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from orders.models import Order


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class TransactionStatus(models.TextChoices):
    WAITING = "waiting", _("Waiting")
    SUCCESS = "success", _("Success")
    FAILED = "failed", _("Failed")
    CANCELLED = "cancelled", _("Cancelled")


class Transaction(BaseModel):
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.PositiveBigIntegerField(verbose_name=_("Amount"))
    currency = models.CharField(max_length=5, blank=True, null=True)
    status = models.CharField(
        max_length=255,
        choices=TransactionStatus.choices,
        default=TransactionStatus.WAITING,
    )
    payment_time = models.DateTimeField(null=True)
    payment_url = models.URLField(
        verbose_name=_("Payment url"), null=True, blank=True, max_length=1255
    )

    def process_after_succesful_payment(self, tr_id):
        order = self.order
        with db_transaction.atomic():
            self.transaction_id = tr_id
            self.status = TransactionStatus.SUCCESS
            self.payment_time = timezone.now()
            self.save()

            # cancel all other waiting transactions
            order.transactions.filter(status=TransactionStatus.WAITING).exclude(
                id=self.id
            ).update(status=TransactionStatus.CANCELLED)

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

    def __str__(self):
        return f"#{self.id} - {self.amount} - {self.status}"
