from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .agents import (
    BrandGuardrailAgent,
    CostEstimatorRAGAgent,
    DesignGeneratorAgent,
    StyleClassifierAgent,
)


class GuardrailCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        text = request.data.get("prompt", "")
        result = BrandGuardrailAgent.check_prompt(text)
        http_status = status.HTTP_200_OK if result["is_safe"] else status.HTTP_400_BAD_REQUEST
        return Response(result, status=http_status)


class StyleAnalyzeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        result = StyleClassifierAgent.classify(
            prompt=request.data.get("prompt", ""),
            image_url=request.data.get("image_url", ""),
        )
        if result.get("blocked"):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


class CostEstimateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response(CostEstimatorRAGAgent.estimate(request.data))


class GenerateDesignView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        mode = request.data.get("mode", "sample")
        result = DesignGeneratorAgent.generate(prompt=request.data.get("prompt", ""), mode=mode)
        if result.get("blocked"):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)
