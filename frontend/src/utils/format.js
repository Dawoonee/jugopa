// 숫자/등락 포맷 유틸 (한국 관행: 상승=빨강 up / 하락=파랑 down)

export function formatNumber(value, decimals = 0) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '-'
  return Number(value).toLocaleString('ko-KR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
}

export function formatSignedRate(rate) {
  if (rate === null || rate === undefined) return '-'
  const v = Number(rate)
  const sign = v > 0 ? '+' : ''
  return `${sign}${v.toFixed(2)}%`
}

export function formatSignedNumber(value, decimals = 0) {
  if (value === null || value === undefined) return '-'
  const v = Number(value)
  const sign = v > 0 ? '+' : ''
  return `${sign}${formatNumber(v, decimals)}`
}

// 등락 방향 → CSS 클래스 (up=빨강 / down=파랑 / flat)
export function changeClass(value) {
  const v = Number(value)
  if (v > 0) return 'up'
  if (v < 0) return 'down'
  return 'flat'
}

export function formatDate(d = new Date()) {
  const date = typeof d === 'string' ? new Date(d) : d
  const days = ['일', '월', '화', '수', '목', '금', '토']
  return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일 ${days[date.getDay()]}`
}
