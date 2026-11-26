from django.urls import path

from .views import TestPGChargeView, WalletDetailView

urlpatterns = [
    path("wallet/", WalletDetailView.as_view(), name="wallet-detail"),
    path("charge/confirm/", TestPGChargeView.as_view(), name="pg-charge-confirm"),
]
