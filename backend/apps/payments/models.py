from django.conf import settings
from django.db import models


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    cash_balance = models.PositiveIntegerField(default=0)
    point_balance = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "wallets"


class LedgerTransaction(models.Model):
    class TxType(models.TextChoices):
        PG_CHARGE = "PG_CHARGE", "PG 캐시 충전"
        DEPOSIT_HOLD = "DEPOSIT_HOLD", "공구 예치금 홀드"
        DIFF_REFUND_POINT = "DIFF_REFUND_POINT", "낙찰 차액 포인트 환급"
        DIFF_REFUND_CASH = "DIFF_REFUND_CASH", "낙찰 차액 캐시 환급"
        LICENSE_PURCHASE = "LICENSE_PURCHASE", "디자인 이용권 구매"
        LICENSE_PAYOUT = "LICENSE_PAYOUT", "디자인 이용권 수익 정산"
        PLATFORM_FEE = "PLATFORM_FEE", "플랫폼 수수료"

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    tx_type = models.CharField(max_length=30, choices=TxType.choices)
    amount = models.IntegerField()
    balance_after = models.PositiveIntegerField()
    pg_tid = models.CharField(max_length=120, blank=True, default="")
    reference_type = models.CharField(max_length=50, blank=True, default="")
    reference_id = models.PositiveBigIntegerField(null=True, blank=True)
    note = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ledger_transactions"
        ordering = ["-created_at"]
