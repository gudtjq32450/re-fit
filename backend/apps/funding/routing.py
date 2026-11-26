from django.urls import re_path

from .consumers import CampaignTrackingConsumer

websocket_urlpatterns = [
    re_path(r"ws/campaigns/(?P<campaign_id>\d+)/$", CampaignTrackingConsumer.as_asgi()),
]
