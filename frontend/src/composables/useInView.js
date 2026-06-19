import { ref, onMounted, onBeforeUnmount } from 'vue'

/**
 * 요소가 뷰포트에 들어오면 inView=true (게이지 채움 애니메이션 트리거용).
 */
export function useInView({ once = true, threshold = 0.2 } = {}) {
  const el = ref(null)
  const inView = ref(false)
  let observer = null

  onMounted(() => {
    if (!('IntersectionObserver' in window)) {
      inView.value = true
      return
    }
    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            inView.value = true
            if (once && observer) observer.disconnect()
          } else if (!once) {
            inView.value = false
          }
        })
      },
      { threshold },
    )
    if (el.value) observer.observe(el.value)
  })

  onBeforeUnmount(() => observer?.disconnect())

  return { el, inView }
}
