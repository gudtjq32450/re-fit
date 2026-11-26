from django.urls import path

from .views import (
    CostEstimateView,
    GenerateDesignView,
    GuardrailCheckView,
    StyleAnalyzeView,
)

urlpatterns = [
    path("guardrail-check/", GuardrailCheckView.as_view(), name="ai-guardrail"),
    path("style-analyze/", StyleAnalyzeView.as_view(), name="ai-style-analyze"),
    path("estimate-cost/", CostEstimateView.as_view(), name="ai-estimate-cost"),
    path("generate-sample/", GenerateDesignView.as_view(), name="ai-generate-sample"),
]
