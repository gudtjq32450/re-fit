from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone


def default_early_bird_deadline():
    return timezone.now() + timedelta(days=7)


class GroupBuyCampaign(models.Model):
    class Status(models.TextChoices):
        RECRUITING = "RECRUITING", "구매 예정자 모집 중"
        BIDDING_OPEN = "BIDDING_OPEN", "공급업체 입찰 가능"
        SUPPLIER_SELECTED = "SUPPLIER_SELECTED", "공급업체 선정 완료"
        IN_PRODUCTION = "IN_PRODUCTION", "제작 진행 중"
        SHIPPED = "SHIPPED", "발송 완료"
        COMPLETED = "COMPLETED", "완료"
        CANCELED = "CANCELED", "취소"

    design = models.OneToOneField(
        "designs.CustomDesign", on_delete=models.CASCADE, related_name="campaign"
    )
    min_participants = models.PositiveIntegerField(default=100)
    current_participants = models.PositiveIntegerField(default=0)
    estimated_unit_cost = models.PositiveIntegerField()
    deposit_price = models.PositiveIntegerField()
    early_bird_deadline = models.DateTimeField(default=default_early_bird_deadline)
    final_unit_cost = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.RECRUITING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "groupbuy_campaigns"
        ordering = ["-created_at"]


class GroupBuyParticipation(models.Model):
    class Size(models.TextChoices):
        XS = "XS", "XS"
        S = "S", "S"
        M = "M", "M"
        L = "L", "L"
        XL = "XL", "XL"
        XXL = "2XL", "2XL"
        XXXL = "3XL", "3XL"

    class Status(models.TextChoices):
        RESERVED = "RESERVED", "구매 예정 확정"
        SETTLED = "SETTLED", "정산 완료"
        REFUNDED = "REFUNDED", "환불 완료"
        CANCELED = "CANCELED", "취소"

    campaign = models.ForeignKey(
        GroupBuyCampaign, on_delete=models.CASCADE, related_name="participations"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="participations")
    selected_size = models.CharField(max_length=10, choices=Size.choices, default=Size.L)
    quantity = models.PositiveIntegerField(default=1)
    deposit_amount = models.PositiveIntegerField()
    service_fee = models.PositiveIntegerField(default=0)
    is_early_bird = models.BooleanField(default=False)
    refunded_amount = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RESERVED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "groupbuy_participations"


class SupplierBid(models.Model):
    campaign = models.ForeignKey(GroupBuyCampaign, on_delete=models.CASCADE, related_name="bids")
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bids")
    proposed_unit_cost = models.PositiveIntegerField()
    estimated_lead_days = models.PositiveIntegerField(default=14)
    proposal_note = models.TextField(blank=True, default="")
    is_selected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "supplier_bids"
        ordering = ["proposed_unit_cost", "created_at"]


class ProductionMilestone(models.Model):
    class Stage(models.TextChoices):
        SUPPLIER_MATCHED = "SUPPLIER_MATCHED", "공급업체 선정"
        FABRIC_ORDERED = "FABRIC_ORDERED", "원단 발주"
        SEWING = "SEWING", "봉제 제작"
        PRINTING = "PRINTING", "프린팅 / 후가공"
        QUALITY_CHECK = "QUALITY_CHECK", "품질 검수"
        SHIPPED = "SHIPPED", "발송 완료"
        DELIVERED = "DELIVERED", "배송 완료"

    campaign = models.ForeignKey(GroupBuyCampaign, on_delete=models.CASCADE, related_name="milestones")
    stage = models.CharField(max_length=30, choices=Stage.choices)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    evidence_image_url = models.URLField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "production_milestones"
        ordering = ["created_at"]
