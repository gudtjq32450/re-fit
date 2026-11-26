from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "USER", "일반 유저 / 디자이너"
        SUPPLIER = "SUPPLIER", "공급업체"
        ADMIN = "ADMIN", "관리자"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    company_name = models.CharField(max_length=100, blank=True, default="")
    business_reg_no = models.CharField(max_length=30, blank=True, default="")
    profile_image = models.URLField(max_length=500, blank=True, default="")
    bio = models.TextField(blank=True, default="")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_set")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_set")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "follows"
        unique_together = ("follower", "following")
