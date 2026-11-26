from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/accounts/", include("apps.accounts.urls")),
    path("api/v1/ai/", include("apps.ai_engine.urls")),
    path("api/v1/designs/", include("apps.designs.urls")),
    path("api/v1/payments/", include("apps.payments.urls")),
    path("api/v1/funding/", include("apps.funding.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
