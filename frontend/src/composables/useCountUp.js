import { ref, watch } from 'vue'

/**
 * 숫자 카운트업 — target 값으로 부드럽게 증가. reduced-motion이면 즉시 반영.
 */
export function useCountUp(target, { duration = 600, decimals = 0 } = {}) {
  const display = ref(0)
  const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

  function animate(to) {
    const from = Number(display.value) || 0
    const end = Number(to) || 0
    if (reduce || from === end) {
      display.value = end.toFixed(decimals)
      return
    }
    const start = performance.now()
    function step(now) {
      const p = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - p, 3) // easeOutCubic
      display.value = (from + (end - from) * eased).toFixed(decimals)
      if (p < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }

  watch(
    () => (typeof target === 'function' ? target() : target?.value ?? target),
    (v) => animate(v),
    { immediate: true },
  )

  return { display }
}
