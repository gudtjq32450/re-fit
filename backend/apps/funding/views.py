from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.models import LedgerTransaction, Wallet
from .models import (
    GroupBuyCampaign,
    GroupBuyParticipation,
    ProductionMilestone,
    SupplierBid,
)


def broadcast_campaign_event(campaign_id: int, event_type: str, data: dict):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        f"campaign_{campaign_id}",
        {"type": "campaign.event", "payload": {"event": event_type, "data": data}},
    )


class SupplierBidSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.company_name", read_only=True)

    class Meta:
        model = SupplierBid
        fields = "__all__"
        read_only_fields = ("campaign", "supplier", "is_selected", "created_at")


class ProductionMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionMilestone
        fields = "__all__"
        read_only_fields = ("campaign", "created_at")


class GroupBuyCampaignSerializer(serializers.ModelSerializer):
    bids = SupplierBidSerializer(many=True, read_only=True)
    milestones = ProductionMilestoneSerializer(many=True, read_only=True)

    class Meta:
        model = GroupBuyCampaign
        fields = "__all__"


class CampaignListCreateView(generics.ListCreateAPIView):
    queryset = GroupBuyCampaign.objects.select_related("design").all()
    serializer_class = GroupBuyCampaignSerializer


class CampaignDetailView(generics.RetrieveAPIView):
    queryset = GroupBuyCampaign.objects.prefetch_related("bids", "milestones").all()
    serializer_class = GroupBuyCampaignSerializer
    permission_classes = [permissions.AllowAny]


class ParticipateCampaignView(APIView):
    """선충전 예치금 홀드 + 1주일 이내 얼리버드 수수료 감면 + 목표 인원 도달 시 입찰 자동 오픈."""

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        campaign = get_object_or_404(GroupBuyCampaign.objects.select_for_update(), pk=pk)
        if campaign.status not in (
            GroupBuyCampaign.Status.RECRUITING,
            GroupBuyCampaign.Status.BIDDING_OPEN,
        ):
            return Response({"detail": "현재 참여할 수 없는 캠페인 상태입니다."}, status=status.HTTP_400_BAD_REQUEST)

        quantity = int(request.data.get("quantity", 1))
        selected_size = request.data.get("selected_size", GroupBuyParticipation.Size.L)
        is_early_bird = timezone.now() <= campaign.early_bird_deadline

        # 얼리버드(등록 후 1주일 이내) 시 플랫폼 수수료 감면
        unit_fee = 0 if is_early_bird else int(campaign.estimated_unit_cost * 0.05)
        total_deposit = campaign.deposit_price * quantity

        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
        if wallet.cash_balance < total_deposit:
            return Response({"detail": "캐시 잔액이 부족합니다. 먼저 캐시를 충전해 주세요."}, status=status.HTTP_400_BAD_REQUEST)

        wallet.cash_balance -= total_deposit
        wallet.save(update_fields=["cash_balance", "updated_at"])

        LedgerTransaction.objects.create(
            wallet=wallet,
            tx_type=LedgerTransaction.TxType.DEPOSIT_HOLD,
            amount=-total_deposit,
            balance_after=wallet.cash_balance,
            reference_type="GroupBuyCampaign",
            reference_id=campaign.id,
            note=f"공구 예치금 홀드 (얼리버드={is_early_bird})",
        )

        participation = GroupBuyParticipation.objects.create(
            campaign=campaign,
            user=request.user,
            selected_size=selected_size,
            quantity=quantity,
            deposit_amount=total_deposit,
            service_fee=unit_fee * quantity,
            is_early_bird=is_early_bird,
        )

        campaign.current_participants += quantity
        if campaign.current_participants >= campaign.min_participants and campaign.status == GroupBuyCampaign.Status.RECRUITING:
            campaign.status = GroupBuyCampaign.Status.BIDDING_OPEN
        campaign.save(update_fields=["current_participants", "status"])

        broadcast_campaign_event(
            campaign.id,
            "PARTICIPATION_UPDATED",
            {
                "current_participants": campaign.current_participants,
                "min_participants": campaign.min_participants,
                "status": campaign.status,
            },
        )
        return Response(
            {
                "participation_id": participation.id,
                "is_early_bird": is_early_bird,
                "deposit_amount": total_deposit,
                "service_fee": participation.service_fee,
                "campaign_status": campaign.status,
            },
            status=status.HTTP_201_CREATED,
        )


class SubmitBidView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if request.user.role != "SUPPLIER":
            return Response({"detail": "공급업체 계정만 입찰할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
        campaign = get_object_or_404(GroupBuyCampaign, pk=pk)
        if campaign.status != GroupBuyCampaign.Status.BIDDING_OPEN:
            return Response({"detail": "최소 구매 예정자 수 달성 후 입찰이 가능합니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SupplierBidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bid = serializer.save(campaign=campaign, supplier=request.user)
        broadcast_campaign_event(campaign.id, "BID_SUBMITTED", SupplierBidSerializer(bid).data)
        return Response(SupplierBidSerializer(bid).data, status=status.HTTP_201_CREATED)


class SelectSupplierBidView(APIView):
    """디자인 등록자가 공급업체 최종 선정 + 예치금 대비 최종 단가 차액 자동 포인트 환급."""

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk, bid_id):
        campaign = get_object_or_404(GroupBuyCampaign.objects.select_for_update(), pk=pk)
        if campaign.design.creator != request.user:
            return Response({"detail": "디자인 등록자만 공급업체를 선정할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

        bid = get_object_or_404(SupplierBid, pk=bid_id, campaign=campaign)
        bid.is_selected = True
        bid.save(update_fields=["is_selected"])

        campaign.final_unit_cost = bid.proposed_unit_cost
        campaign.status = GroupBuyCampaign.Status.SUPPLIER_SELECTED
        campaign.save(update_fields=["final_unit_cost", "status"])

        total_refunded = 0
        for p in campaign.participations.select_for_update().filter(status=GroupBuyParticipation.Status.RESERVED):
            final_total = (bid.proposed_unit_cost * p.quantity) + p.service_fee
            diff = max(0, p.deposit_amount - final_total)
            if diff > 0:
                wallet, _ = Wallet.objects.select_for_update().get_or_create(user=p.user)
                wallet.point_balance += diff
                wallet.save(update_fields=["point_balance", "updated_at"])
                LedgerTransaction.objects.create(
                    wallet=wallet,
                    tx_type=LedgerTransaction.TxType.DIFF_REFUND_POINT,
                    amount=diff,
                    balance_after=wallet.point_balance,
                    reference_type="GroupBuyCampaign",
                    reference_id=campaign.id,
                    note=f"공급업체 낙찰 단가({bid.proposed_unit_cost:,}원) 차액 포인트 환급",
                )
                p.refunded_amount = diff
                total_refunded += diff
            p.status = GroupBuyParticipation.Status.SETTLED
            p.save(update_fields=["refunded_amount", "status"])

        ProductionMilestone.objects.create(
            campaign=campaign,
            stage=ProductionMilestone.Stage.SUPPLIER_MATCHED,
            title="공급업체 선정 및 차액 정산 완료",
            description=f"최종 단가 {bid.proposed_unit_cost:,}원으로 제작이 확정되었습니다.",
        )

        broadcast_campaign_event(
            campaign.id,
            "SUPPLIER_SELECTED",
            {"bid_id": bid.id, "final_unit_cost": bid.proposed_unit_cost, "total_refunded": total_refunded},
        )
        return Response(
            {"selected_bid_id": bid.id, "final_unit_cost": bid.proposed_unit_cost, "total_refunded": total_refunded}
        )


class AddMilestoneView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        campaign = get_object_or_404(GroupBuyCampaign, pk=pk)
        serializer = ProductionMilestoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        milestone = serializer.save(campaign=campaign)
        broadcast_campaign_event(campaign.id, "MILESTONE_UPDATED", ProductionMilestoneSerializer(milestone).data)
        return Response(ProductionMilestoneSerializer(milestone).data, status=status.HTTP_201_CREATED)
