<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { stocksApi } from '@/api/stocks'

const router = useRouter()

const query = ref('')
const results = ref([])
const loading = ref(false)
const searched = ref(false)
const open = ref(false)
let debounceId = null

watch(query, (q) => {
  const term = q.trim()
  clearTimeout(debounceId)
  if (!term) {
    results.value = []
    searched.value = false
    open.value = false
    return
  }
  debounceId = setTimeout(() => runSearch(term), 250)
})

async function runSearch(term) {
  loading.value = true
  open.value = true
  try {
    const { data } = await stocksApi.search(term)
    results.value = data
  } catch (e) {
    results.value = []
  } finally {
    loading.value = false
    searched.value = true
  }
}

function goTo(stock) {
  if (!stock) return
  open.value = false
  query.value = ''
  results.value = []
  searched.value = false
  router.push({ name: 'stock-detail', params: { code: stock.stock_code } })
}

function onEnter() {
  if (results.value.length) goTo(results.value[0])
}

function onBlur() {
  // 항목 클릭이 먼저 처리되도록 약간 지연 후 닫기
  setTimeout(() => {
    open.value = false
  }, 150)
}
</script>

<template>
  <div class="search">
    <div class="search-box">
      <span class="search-icon">🔍</span>
      <input
        v-model="query"
        class="search-input"
        type="text"
        placeholder="종목명 검색 (예: 삼성전자, 카카오)"
        autocomplete="off"
        @focus="query.trim() && (open = true)"
        @blur="onBlur"
        @keydown.enter="onEnter"
      />
    </div>

    <div v-if="open" class="dropdown card">
      <p v-if="loading" class="hint">검색 중…</p>
      <ul v-else-if="results.length" class="result-list">
        <li
          v-for="s in results"
          :key="s.stock_code"
          class="result-item"
          @mousedown.prevent="goTo(s)"
        >
          <span class="result-name">{{ s.stock_name }}</span>
          <span class="result-code num">{{ s.stock_code }} · {{ s.market_type }}</span>
        </li>
      </ul>
      <p v-else-if="searched" class="hint">검색 결과가 없어요</p>
    </div>
  </div>
</template>

<style scoped>
.search {
  position: relative;
  margin-bottom: var(--space-6);
}
.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  transition: border-color var(--dur-fast), box-shadow var(--dur-fast);
}
.search-box:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}
.search-icon {
  font-size: 15px;
  opacity: 0.7;
}
.search-input {
  flex: 1;
  padding: 13px 0;
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 15px;
}
.search-input::placeholder {
  color: var(--text-tertiary);
}
.search-input:focus {
  outline: none;
}
.dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  z-index: 20;
  padding: var(--space-2);
  max-height: 320px;
  overflow-y: auto;
}
.hint {
  padding: 12px var(--space-3);
  color: var(--text-tertiary);
  font-size: 14px;
}
.result-list {
  display: flex;
  flex-direction: column;
}
.result-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 12px var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--dur-fast);
}
.result-item:hover {
  background: var(--bg-hover);
}
.result-name {
  font-weight: 700;
}
.result-code {
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>
