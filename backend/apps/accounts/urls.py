from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import FollowToggleView, MeView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="account-register"),
    path("login/", TokenObtainPairView.as_view(), name="account-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="account-me"),
    path("<int:user_id>/follow/", FollowToggleView.as_view(), name="account-follow"),
]
