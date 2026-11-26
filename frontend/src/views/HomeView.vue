<template>
  <section class="hero">
    <p class="eyebrow">Design it. Fund it. Wear it.</p>
    <h1>RE:FIT</h1>
    <p class="slogan">Don't fit in. RE:FIT.</p>
    <p class="subtitle">
      세상의 기준에 맞추지 말고, 당신만의 핏을 만드세요.<br />
      AI 커스텀 디자인부터 크라우드 펀딩 공구·공급업체 입찰·제작 공개까지.
    </p>
    <RouterLink to="/studio" class="cta-btn">3D 커스텀 스튜디오 시작하기</RouterLink>
  </section>
</template>

<style scoped>
.hero {
  max-width: 780px;
  margin: 80px auto;
  text-align: center;
  padding: 0 20px;
}
.eyebrow {
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-size: 0.85rem;
  color: #94a3b8;
}
h1 {
  font-size: 3.5rem;
  margin: 12px 0 6px;
}
.slogan {
  font-size: 1.35rem;
  font-weight: 700;
  color: #38bdf8;
  margin-bottom: 16px;
}
.subtitle {
  color: #cbd5e1;
  line-height: 1.7;
  margin-bottom: 32px;
}
.cta-btn {
  display: inline-block;
  padding: 14px 28px;
  border-radius: 999px;
  background: #f8fafc;
  color: #0f172a;
  font-weight: 700;
  text-decoration: none;
}
</style>
