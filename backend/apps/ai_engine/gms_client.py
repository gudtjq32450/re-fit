from django.conf import settings
from openai import OpenAI


def get_gms_client() -> OpenAI | None:
    """Return an OpenAI-compatible client pointing to SSAFY GMS Gateway."""
    if settings.AI_MOCK_MODE or not settings.GMS_API_KEY:
        return None
    return OpenAI(
        api_key=settings.GMS_API_KEY,
        base_url=settings.GMS_BASE_URL,
    )
