from django.urls import path

from .views import (
    AddMilestoneView,
    CampaignDetailView,
    CampaignListCreateView,
    ParticipateCampaignView,
    SelectSupplierBidView,
    SubmitBidView,
)

urlpatterns = [
    path("campaigns/", CampaignListCreateView.as_view(), name="campaign-list-create"),
    path("campaigns/<int:pk>/", CampaignDetailView.as_view(), name="campaign-detail"),
    path("campaigns/<int:pk>/participate/", ParticipateCampaignView.as_view(), name="campaign-participate"),
    path("campaigns/<int:pk>/bids/", SubmitBidView.as_view(), name="campaign-bid-submit"),
    path("campaigns/<int:pk>/bids/<int:bid_id>/select/", SelectSupplierBidView.as_view(), name="campaign-bid-select"),
    path("campaigns/<int:pk>/milestones/", AddMilestoneView.as_view(), name="campaign-milestone-add"),
]
