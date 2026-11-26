from django.conf import settings
from django.db import models


class StyleCategory(models.Model):
    parent_category = models.CharField(max_length=50)
    name = models.CharField(max_length=80, unique=True)
    keywords = models.JSONField(default=list)

    class Meta:
        db_table = "style_categories"

    def __str__(self):
        return f"{self.parent_category} - {self.name}"


class StyleReference(models.Model):
    style = models.ForeignKey(StyleCategory, on_delete=models.CASCADE, related_name="references")
    image_url = models.URLField(max_length=500)
    tags = models.JSONField(default=list)

    class Meta:
        db_table = "style_references"


class GarmentTemplate(models.Model):
    class GarmentType(models.TextChoices):
        TSHIRT = "TSHIRT", "티셔츠"
        SWEATSHIRT = "SWEATSHIRT", "맨투맨"
        HOODIE = "HOODIE", "후드티"
        WINDBREAKER = "WINDBREAKER", "바람막이"
        PADDING = "PADDING", "패딩"
        COAT = "COAT", "코트"
        UNIFORM = "UNIFORM", "유니폼 (레거시)"

    garment_type = models.CharField(max_length=30, choices=GarmentType.choices)
    name = models.CharField(max_length=100)
    is_legacy_copyrighted = models.BooleanField(default=False)
    model_glb_url = models.URLField(max_length=500, blank=True, default="")
    base_labor_cost = models.PositiveIntegerField(default=18000)
    size_chart = models.JSONField(default=dict)

    class Meta:
        db_table = "garment_templates"


class FabricMaterial(models.Model):
    name = models.CharField(max_length=100)
    gsm_weight = models.PositiveIntegerField(default=320)
    thickness_level = models.PositiveSmallIntegerField(default=3)
    wrinkle_level = models.PositiveSmallIntegerField(default=2)
    cost_per_unit = models.PositiveIntegerField(default=20000)
    pbr_textures = models.JSONField(default=dict)

    class Meta:
        db_table = "fabric_materials"


class CustomDesign(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "임시저장"
        PUBLISHED = "PUBLISHED", "공개됨"
        BLINDED = "BLINDED", "위조품 차단"

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="designs")
    template = models.ForeignKey(GarmentTemplate, on_delete=models.PROTECT, null=True, blank=True)
    style = models.ForeignKey(StyleCategory, on_delete=models.SET_NULL, null=True, blank=True)
    outer_fabric = models.ForeignKey(
        FabricMaterial, on_delete=models.PROTECT, related_name="outer_designs", null=True, blank=True
    )
    inner_fabric = models.ForeignKey(
        FabricMaterial, on_delete=models.PROTECT, related_name="inner_designs", null=True, blank=True
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, default="")
    prompt_history = models.JSONField(default=list)
    custom_spec = models.JSONField(default=dict)
    preview_image_url = models.URLField(max_length=500, blank=True, default="")
    estimated_cost = models.PositiveIntegerField(default=0)
    cost_breakdown = models.JSONField(default=dict)
    license_price = models.PositiveIntegerField(default=0)
    copyright_owner = models.CharField(max_length=50, default="RE:FIT")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PUBLISHED)
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "custom_designs"
        ordering = ["-created_at"]


class DesignLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    design = models.ForeignKey(CustomDesign, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "design_likes"
        unique_together = ("user", "design")


class DesignLicense(models.Model):
    design = models.ForeignKey(CustomDesign, on_delete=models.CASCADE, related_name="licenses")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchased_licenses")
    paid_amount = models.PositiveIntegerField()
    platform_fee = models.PositiveIntegerField()
    creator_payout = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "design_licenses"
