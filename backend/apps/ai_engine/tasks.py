from celery import shared_task

from apps.designs.models import CustomDesign
from .agents import BrandGuardrailAgent


@shared_task
def run_periodic_counterfeit_scan():
    """2차 사후 관리: 우회 등록된 유명 브랜드 위조품 시안을 주기적으로 탐지하여 블라인드 처리."""
    flagged_count = 0
    for design in CustomDesign.objects.filter(status=CustomDesign.Status.PUBLISHED):
        combined_text = f"{design.title} {design.description} {' '.join(map(str, design.prompt_history))}"
        result = BrandGuardrailAgent.check_prompt(combined_text)
        if not result["is_safe"]:
            design.status = CustomDesign.Status.BLINDED
            design.save(update_fields=["status"])
            flagged_count += 1
    return {"scanned_and_blinded": flagged_count}
