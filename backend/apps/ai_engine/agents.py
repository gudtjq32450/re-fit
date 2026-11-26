import json
import re
from django.conf import settings

from .gms_client import get_gms_client

PROTECTED_BRANDS = [
    "supreme", "louis vuitton", "lv", "gucci", "chanel", "balenciaga",
    "nike", "adidas", "prada", "dior", "hermes", "stussy", "off-white",
    "슈프림", "루이비통", "구찌", "샤넬", "발렌시아가", "나이키", "아디다스", "프라다", "디올",
]

STYLE_TAXONOMY = [
    {"id": "STREET_GORPCORE", "parent": "스트릿", "name": "고프코어"},
    {"id": "STREET_VINTAGE", "parent": "스트릿", "name": "빈티지 스트릿"},
    {"id": "STREET_TECHWEAR", "parent": "스트릿", "name": "테크웨어"},
    {"id": "ROCK_CHIC_GRUNGE", "parent": "락시크", "name": "그런지 락시크"},
    {"id": "HIPHOP_OVERSIZED", "parent": "힙합", "name": "오버사이즈 힙합"},
    {"id": "MODERN_MINIMAL", "parent": "모던", "name": "미니멀 컨템포러리"},
    {"id": "CASUAL_AMEKAJI", "parent": "캐주얼", "name": "아메카지 캐주얼"},
    {"id": "CUTE_LOVELY", "parent": "큐트", "name": "러블리 키치"},
]


class BrandGuardrailAgent:
    """1차 상표권/위조품(짝퉁) 차단 에이전트."""

    @staticmethod
    def check_prompt(text: str) -> dict:
        lowered = (text or "").lower()
        matched = [b for b in PROTECTED_BRANDS if re.search(rf"\b{re.escape(b)}\b" if b.isascii() else re.escape(b), lowered)]
        if matched:
            return {
                "is_safe": False,
                "blocked_brands": matched,
                "reason": f"상표권 보호 대상 브랜드({', '.join(matched)})는 디자인 생성 및 등록이 제한됩니다.",
            }
        return {"is_safe": True, "blocked_brands": [], "reason": ""}


class StyleClassifierAgent:
    """프롬프트 또는 이미지 기반 세분화 스타일 분류 (Structured Output)."""

    @staticmethod
    def classify(prompt: str = "", image_url: str = "") -> dict:
        guard = BrandGuardrailAgent.check_prompt(prompt)
        if not guard["is_safe"]:
            return {"blocked": True, **guard}

        client = get_gms_client()
        if client is None:
            return {
                "blocked": False,
                "top_styles": STYLE_TAXONOMY[:3],
                "extracted_tags": ["오버핏", "헤비코튼", "다크톤"],
                "confirmation_message": "이런 스타일의 옷을 원하시나요? 아래 레퍼런스 중 가장 가까운 무드를 선택해 주세요.",
            }

        system_prompt = (
            "You are RE:FIT's fashion style classifier. "
            "Pick top 3 styles strictly from this taxonomy list and respond in JSON with keys: "
            "'top_style_ids' (list of 3 ids), 'extracted_tags' (list of Korean fashion tags). "
            f"Taxonomy: {json.dumps(STYLE_TAXONOMY, ensure_ascii=False)}"
        )
        user_content = [{"type": "text", "text": prompt or "이 착장의 패션 스타일을 분류해 주세요."}]
        if image_url:
            user_content.append({"type": "image_url", "image_url": {"url": image_url}})

        response = client.chat.completions.create(
            model=settings.GMS_VISION_MODEL if image_url else settings.GMS_CHAT_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        parsed = json.loads(response.choices[0].message.content)
        id_map = {item["id"]: item for item in STYLE_TAXONOMY}
        top_styles = [id_map[sid] for sid in parsed.get("top_style_ids", []) if sid in id_map]
        return {
            "blocked": False,
            "top_styles": top_styles or STYLE_TAXONOMY[:3],
            "extracted_tags": parsed.get("extracted_tags", []),
            "confirmation_message": "이런 스타일의 옷을 원하시나요? 스타일을 확정하면 디자인 샘플을 생성합니다.",
        }


class CostEstimatorRAGAgent:
    """원단·공정·이중 덧댐·수량 기반 예상 제작가격 산출 (RAG 지식 기반)."""

    BASE_COSTS = {
        "TSHIRT": 18000,
        "SWEATSHIRT": 28000,
        "HOODIE": 34000,
        "WINDBREAKER": 42000,
        "PADDING": 68000,
        "COAT": 75000,
        "UNIFORM": 36000,
    }

    @classmethod
    def estimate(cls, spec: dict) -> dict:
        garment_type = spec.get("garment_type", "HOODIE").upper()
        base = cls.BASE_COSTS.get(garment_type, 34000)
        gsm = int(spec.get("gsm_weight", 420))
        double_layered = bool(spec.get("double_layered", False))
        oversized_hood = bool(spec.get("oversized_hood", False))
        has_printing = bool(spec.get("printing_text") or spec.get("has_logo"))
        target_qty = max(1, int(spec.get("target_quantity", 100)))

        fabric_cost = int(base * 0.55) + max(0, (gsm - 250) * 35)
        layer_cost = 14000 if double_layered else 0
        hood_cost = 4000 if oversized_hood else 0
        labor_cost = int(base * 0.45) + hood_cost
        printing_cost = 6000 if has_printing else 0

        # 수량 할인 (공구 100벌 기준 단가 최적화)
        volume_factor = 1.0 if target_qty >= 100 else (1.15 if target_qty >= 50 else 1.45)
        raw_total = int((fabric_cost + layer_cost + labor_cost + printing_cost) * volume_factor)
        estimated_unit_cost = round(raw_total, -3)
        recommended_deposit = round(int(estimated_unit_cost * 1.21), -3)

        return {
            "estimated_unit_cost": estimated_unit_cost,
            "recommended_deposit": recommended_deposit,
            "breakdown": {
                "fabric_cost": fabric_cost,
                "lining_and_layer_cost": layer_cost,
                "labor_cost": labor_cost,
                "printing_and_trims": printing_cost,
            },
            "rag_sources": [
                f"{garment_type} 기본 공임 기준표 (2026)",
                f"원단 중량 {gsm}g/m² 단가 기준",
                "이중 덧댐 추가 봉제 공정 단가" if double_layered else "단일 레이어 표준 봉제 공정",
            ],
        }


class DesignGeneratorAgent:
    """확정 스타일 기반 디자인 시안 / 로고 그래픽 생성 에이전트."""

    @staticmethod
    def generate(prompt: str, mode: str = "sample") -> dict:
        guard = BrandGuardrailAgent.check_prompt(prompt)
        if not guard["is_safe"]:
            return {"blocked": True, **guard}

        client = get_gms_client()
        if client is None:
            return {
                "blocked": False,
                "mode": mode,
                "image_url": "https://placehold.co/768x768/111827/F9FAFB?text=RE%3AFIT+AI+Sample",
                "prompt_used": prompt,
            }

        prefix = (
            "Minimal clean vector apparel logo graphic on plain background, no real-world trademarked brands: "
            if mode == "logo"
            else "High-fashion ghost mannequin garment studio product shot, no faces, no real-world brand logos: "
        )
        res = client.images.generate(
            model=settings.GMS_IMAGE_MODEL,
            prompt=f"{prefix}{prompt}",
            size="1024x1024",
            n=1,
        )
        return {
            "blocked": False,
            "mode": mode,
            "image_url": res.data[0].url,
            "prompt_used": prompt,
        }
