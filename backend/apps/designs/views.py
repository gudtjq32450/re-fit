from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomDesign, DesignLike, FabricMaterial, GarmentTemplate


class GarmentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GarmentTemplate
        fields = "__all__"


class FabricMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = FabricMaterial
        fields = "__all__"


class CustomDesignSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source="creator.username", read_only=True)

    class Meta:
        model = CustomDesign
        fields = "__all__"
        read_only_fields = ("creator", "copyright_owner", "like_count", "created_at")


class TemplateListView(generics.ListAPIView):
    queryset = GarmentTemplate.objects.all()
    serializer_class = GarmentTemplateSerializer
    permission_classes = [permissions.AllowAny]


class FabricListView(generics.ListAPIView):
    queryset = FabricMaterial.objects.all()
    serializer_class = FabricMaterialSerializer
    permission_classes = [permissions.AllowAny]


class DesignListCreateView(generics.ListCreateAPIView):
    queryset = CustomDesign.objects.filter(status=CustomDesign.Status.PUBLISHED)
    serializer_class = CustomDesignSerializer
    filterset_fields = ("template__garment_type", "style")
    search_fields = ("title", "description")
    ordering_fields = ("created_at", "like_count", "estimated_cost")

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class DesignDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomDesign.objects.all()
    serializer_class = CustomDesignSerializer


class DesignLikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        design = get_object_or_404(CustomDesign, pk=pk)
        like, created = DesignLike.objects.get_or_create(user=request.user, design=design)
        if not created:
            like.delete()
            CustomDesign.objects.filter(pk=pk).update(like_count=F("like_count") - 1)
            return Response({"liked": False})
        CustomDesign.objects.filter(pk=pk).update(like_count=F("like_count") + 1)
        return Response({"liked": True}, status=status.HTTP_201_CREATED)
