# RE:FIT API Specification

* **Base URL:** `/api/v1`
* **Auth:** `Authorization: Bearer <JWT_ACCESS_TOKEN>`
* **Content-Type:** `application/json` *(이미지 업로드는 `multipart/form-data`)*

---

## 1. Auth & Users (`/api/v1/accounts/`)

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/accounts/register/` | Public | 회원가입 (`role`: `USER` 또는 `SUPPLIER`) |
| `POST` | `/accounts/login/` | Public | JWT Access / Refresh 토큰 발급 |
| `POST` | `/accounts/token/refresh/` | Public | Access 토큰 갱신 |
| `GET` / `PATCH` | `/accounts/me/` | Bearer | 내 프로필, 지갑 잔액, 역할 정보 조회/수정 |
| `POST` | `/accounts/{user_id}/follow/` | Bearer | 제작자 팔로우 / 언팔로우 토글 |

---

## 2. AI Multi-Agent & RAG (`/api/v1/ai/`)

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/ai/style-analyze/` | Bearer | 프롬프트 또는 착장 이미지 → 스타일 Top-3 분류 + 레퍼런스 예시 이미지 반환 *(재확인 단계)* |
| `POST` | `/ai/generate-sample/` | Bearer | 확정된 스타일 & 커스텀 옵션 기반 디자인 시안 이미지 생성 *(사전 상표권 Guardrail 포함)* |
| `POST` | `/ai/generate-logo/` | Bearer | 텍스트 프롬프트 → 3D 의류 데칼용 로고 그래픽 생성 *(상표권 Guardrail 포함)* |
| `POST` | `/ai/estimate-cost/` | Bearer | 원단·두께·이중 덧댐·프린팅·수량 기반 **RAG 예상 제작가격 & 상세 견적** 산출 |
| `POST` | `/ai/guardrail-check/` | Bearer | 텍스트/이미지 유명 브랜드(짝퉁) 사전 검증 |

### Example: `POST /api/v1/ai/estimate-cost/`
```json
// Request
{
  "garment_type": "HOODIE",
  "outer_fabric_id": 1,
  "inner_fabric_id": 3,
  "double_layered": true,
  "oversized_hood": true,
  "printing_area": "FRONT_CHEST",
  "target_quantity": 100
}

// Response
{
  "estimated_unit_cost": 70000,
  "recommended_deposit": 85000,
  "breakdown": {
    "fabric_cost": 32000,
    "lining_and_layer_cost": 14000,
    "labor_cost": 18000,
    "printing_and_trims": 6000
  },
  "rag_sources": ["헤비 면 480g 단가표 (2026)", "후드 이중 덧댐 공임 기준"]
}
```

---

## 3. 3D Studio Catalog & Designs CRUD (`/api/v1/designs/`)

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/designs/templates/` | Public | 3D 의류 베이스 템플릿(`.glb`, 사이즈 차트 XS~3XL, 레거시 유니폼) 목록 |
| `GET` | `/designs/fabrics/` | Public | 원단 목록 & PBR 텍스처 맵(질감·두께·구김·무게) |
| `GET` | `/designs/` | Public | 디자인 시안 게시판 목록 (스타일/의류종류/인기순 필터) |
| `POST` | `/designs/` | Bearer | 커스텀 디자인 시안 등록 *(자동으로 상표권 검사 및 공구 캠페인 생성 옵션 지원)* |
| `GET` / `PATCH` / `DELETE` | `/designs/{id}/` | Bearer | 디자인 시안 상세 조회 / 수정 / 삭제 |
| `POST` | `/designs/{id}/like/` | Bearer | 디자인 좋아요 토글 |
| `POST` | `/designs/{id}/license/` | Bearer | 디자인 이용권 구매 (제작자 수익 + 플랫폼 수수료 자동 정산) |

---

## 4. Wallet & Test PG (`/api/v1/payments/`)

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/payments/wallet/` | Bearer | 내 캐시·포인트 잔액 및 원장 거래 내역 조회 |
| `POST` | `/payments/charge/prepare/` | Bearer | 테스트 PG(PortOne/Toss) 충전 주문 생성 |
| `POST` | `/payments/charge/confirm/` | Bearer | PG 결제 검증 완료 후 캐시 적립 (개발용 즉시 테스트 충전 지원) |

---

## 5. Crowdfunding, Bidding & Production Tracking (`/api/v1/funding/`)

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/funding/campaigns/` | Public | 진행 중인 공구 캠페인 목록 (달성률·상태 필터) |
| `GET` | `/funding/campaigns/{id}/` | Public | 캠페인 상세 (예상가, 예치금, 참여자 수, 얼리버드 마감일, 입찰 목록, 공정 타임라인) |
| `POST` | `/funding/campaigns/{id}/participate/` | Bearer | 구매 예정 확정 (예치금 홀드, 등록 1주일 이내 수수료 자동 감면, 목표 달성 시 입찰 자동 오픈) |
| `POST` | `/funding/campaigns/{id}/bids/` | Bearer (`SUPPLIER`) | 최소 인원 돌파 캠페인에 공급업체 입찰가 제출 |
| `POST` | `/funding/campaigns/{id}/bids/{bid_id}/select/` | Bearer (등록자) | 공급업체 최종 선정 & **낙찰 차액 자동 포인트/캐시 환급** |
| `POST` | `/funding/campaigns/{id}/milestones/` | Bearer (선정 업체) | 제작~발송 공정 단계 및 인증샷 등록 → WebSocket 실시간 브로드캐스트 |

---

## 6. Real-Time WebSocket (`/ws/campaigns/{campaign_id}/`)

공구 캠페인 상세 페이지 접속 시 실시간 이벤트를 수신합니다.

```json
// Event Types
// 1) "PARTICIPATION_UPDATED" — 참여자 수 & 달성률 실시간 갱신
// 2) "BID_SUBMITTED"         — 새 공급업체 입찰 도착
// 3) "SUPPLIER_SELECTED"     — 공급업체 확정 및 차액 환급 완료
// 4) "MILESTONE_UPDATED"     — 제작/검수/발송 공정 상태 및 사진 업데이트
```
