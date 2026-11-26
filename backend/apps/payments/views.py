from django.db import transaction
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import LedgerTransaction, Wallet


class LedgerTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerTransaction
        fields = "__all__"


class WalletSerializer(serializers.ModelSerializer):
    transactions = LedgerTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = ("id", "cash_balance", "point_balance", "updated_at", "transactions")


class WalletDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return Response(WalletSerializer(wallet).data)


class TestPGChargeView(APIView):
    """PortOne / Toss Payments 테스트 결제 검증 후 캐시 적립."""

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        amount = int(request.data.get("amount", 0))
        pg_tid = request.data.get("pg_tid", "TEST_PG_TX")
        if amount <= 0:
            return Response({"detail": "충전 금액은 0보다 커야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
        wallet.cash_balance += amount
        wallet.save(update_fields=["cash_balance", "updated_at"])

        LedgerTransaction.objects.create(
            wallet=wallet,
            tx_type=LedgerTransaction.TxType.PG_CHARGE,
            amount=amount,
            balance_after=wallet.cash_balance,
            pg_tid=pg_tid,
            note="테스트 PG 캐시 충전",
        )
        return Response(WalletSerializer(wallet).data, status=status.HTTP_201_CREATED)
