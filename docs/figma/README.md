# RE:FIT Figma UI Kit & Screen Frames (`1440 × 900`)

본 디렉터리는 **RE:FIT**의 핵심 유저 플로우(`Design it → Fund it → Wear it`)와 **인터랙티브 3D 커스텀 스튜디오**의 예상 화면을 Figma에서 즉시 편집할 수 있도록 구조화한 벡터 프레임(`.svg`) 및 디자인 시스템 명세입니다.

---

## 1. Figma로 바로 불러오는 방법 (3초 임포트)

1. Figma 데스크톱 앱 또는 웹(`figma.com`)에서 새 디자인 파일을 엽니다.
2. 아래 `.svg` 파일 3개를 다운로드하여 **Figma 캔버스 위로 그대로 드래그 앤 드롭(Drag & Drop)** 합니다.
3. 각 파일이 **`1440 × 900` 데스크톱 프레임**으로 열리며, 내부의 모든 패널(`TopStudioHeader`, `Garment_Rotation_And_Focus_HUD`, `Left_Tactile_Brush_Toolbar`, `Bottom_Lighting_Simulation_Bar`, `Right_Dual_Customization_Panel` 등)이 **개별 그룹(Group)과 편집 가능한 텍스트 레이어**로 자동 분리됩니다.

| 파일명 | 화면 역할 및 포함 로직 |
| :--- | :--- |
| [`01_Style_Analysis_Frame_1440x900.svg`](./01_Style_Analysis_Frame_1440x900.svg) | **Step 1. AI 스타일 분석 & 재확인:** 착장 이미지/프롬프트 입력, 상표권(짝퉁) Guardrail 배지, *"이런 스타일의 옷을 원하시나요?"* 고스트 마네킹 Top-3 레퍼런스 카드 및 속성 태그 보정 |
| [`02_3D_Interactive_Studio_Frame_1440x900.svg`](./02_3D_Interactive_Studio_Frame_1440x900.svg) | **Step 2. 인터랙티브 3D 커스텀 스튜디오 (핵심 화면):**<br>• **상단 뷰잉 HUD:** 의류 자체 360° 회전·턴테이블·부위별 스냅 줌 (광원 회전과 독립 분리)<br>• **좌측 촉각 브러시 독:** 구기기(Crumple) · 펴기(Smooth) · 옷 회전 · 데칼 이동 · 마찰음 ON/OFF<br>• **하단 채광 바:** 5대 환경(`스튜디오` · `자연광` · `형광등` · `밤거리` · `가로등`) & 광원 360° 회전<br>• **우측 듀얼 패널:** 실시간 AI 프롬프트 입력창 + 세부 스펙 조절창(원단 물성·빅후드·이중덧댐·컬러·폰트·XS~3XL) + RAG 단가 요약 |
| [`03_Funding_And_RAG_Estimate_Frame_1440x900.svg`](./03_Funding_And_RAG_Estimate_Frame_1440x900.svg) | **Step 3. 크라우드 펀딩 공구 & 공급업체 입찰·공정 공개:** 예상가(70,000원) vs 선충전 예치금(85,000원), 등록 1주일 이내 수수료 감면, 100명 돌파 업체 역경매 입찰, 차액 자동 환급 및 제작~발송 실시간 타임라인 |

---

## 2. Figma 디자인 토큰 규격 (Design System Tokens)

### 2.1. Layout & Grid
* **Desktop Frame:** `1440 × 900 px`
* **Studio Split Ratio:** 좌측 3D 아틀리에 뷰포트 `62% (876px)` : 우측 듀얼 커스텀 패널 `35% (500px)` *(3D 작업 시야 극대화)*

### 2.2. Color Palette (Dark Atelier Theme)
* **Canvas Background:** `#090D16` (채광 및 원단 색감 왜곡을 최소화하는 무채색 딥 다크 배경)
* **Surface / Panel Card:** `#111827` (Border `#1E293B`)
* **Primary Brand Accent:** `#38BDF8` (활성 도구, 선택된 사이즈/채광, 주요 CTA)
* **Status Semantic:** `#34D399` (상표권 안전 / 목표 달성 / 차액 환급), `#FACC15` (얼리버드 혜택 / 진행 중 공정), `#F87171` (위조품 차단 경고)

### 2.3. Typography
* **Primary UI Font:** `Pretendard` / `Noto Sans KR` (`800 ExtraBold` 타이틀 · `600~700` 컨트롤 라벨 · `400` 본문)
* **Numeric / Price / Angle Readout:** `JetBrains Mono` (`tabular-nums` 고정폭 숫자 정렬로 슬라이더 및 단가 변화 시 흔들림 방지)
