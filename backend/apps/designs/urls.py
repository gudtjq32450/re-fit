from django.urls import path

from .views import (
    DesignDetailView,
    DesignLikeToggleView,
    DesignListCreateView,
    FabricListView,
    TemplateListView,
)

urlpatterns = [
    path("templates/", TemplateListView.as_view(), name="template-list"),
    path("fabrics/", FabricListView.as_view(), name="fabric-list"),
    path("", DesignListCreateView.as_view(), name="design-list-create"),
    path("<int:pk>/", DesignDetailView.as_view(), name="design-detail"),
    path("<int:pk>/like/", DesignLikeToggleView.as_view(), name="design-like"),
]
