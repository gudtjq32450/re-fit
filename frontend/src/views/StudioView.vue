<template>
  <div class="studio-layout">
    <div class="viewer-pane">
      <GarmentCanvas3D
        :color="store.color"
        :roughness="store.roughness"
        :size="store.size"
        :printing-text="store.printingText"
        :oversized-hood="store.oversizedHood"
      />
    </div>

    <aside class="control-pane">
      <h2>AI 커스텀 스튜디오</h2>

      <label>AI 스타일 프롬프트</label>
      <textarea
        v-model="store.prompt"
        rows="3"
        placeholder="예: 단단한 헤비코튼 오버핏 후드티, 다크 스트릿 무드, 큰 후드"
      />

      <div class="row">
        <div>
          <label>색상</label>
          <input v-model="store.color" type="color" />
        </div>
        <div>
          <label>사이즈 (XS~3XL)</label>
          <select v-model="store.size">
            <option v-for="s in ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL']" :key="s" :value="s">
              {{ s }}
            </option>
          </select>
        </div>
      </div>

      <label>프린팅 문구 (3D 실시간 반영)</label>
      <input v-model="store.printingText" type="text" maxlength="20" />

      <label>원단 거칠기 / 질감 ({{ store.roughness }})</label>
      <input v-model.number="store.roughness" type="range" min="0.2" max="1" step="0.05" />

      <label class="checkbox">
        <input v-model="store.doubleLayered" type="checkbox" /> 겉감 이중 덧댐 + 안감 면
      </label>
      <label class="checkbox">
        <input v-model="store.oversizedHood" type="checkbox" /> 빅 후드 옵션
      </label>

      <div class="price-box">
        <div>예상 제작가: <strong>{{ store.estimatedCost.toLocaleString() }}원</strong></div>
        <div>공구 예치금: <strong>{{ store.recommendedDeposit.toLocaleString() }}원</strong></div>
      </div>

      <button class="action-btn" @click="store.estimateCost()">RAG 예상 제작가 산출</button>
    </aside>
  </div>
</template>

<script setup>
import GarmentCanvas3D from "../components/studio/GarmentCanvas3D.vue";
import { useStudioStore } from "../stores/studio";

const store = useStudioStore();
</script>

<style scoped>
.studio-layout {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 24px;
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 20px;
}
.control-pane {
  background: #1e293b;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
label {
  font-size: 0.85rem;
  color: #cbd5e1;
}
textarea,
input[type="text"],
select {
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #f8fafc;
}
.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
}
.price-box {
  background: #0f172a;
  padding: 14px;
  border-radius: 10px;
  line-height: 1.8;
}
.action-btn {
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: #38bdf8;
  color: #0f172a;
  font-weight: 700;
  cursor: pointer;
}
</style>
