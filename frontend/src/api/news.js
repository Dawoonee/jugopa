import client from './client'

export const newsApi = {
  sectors() {
    return client.get('news/sectors/')
  },
  sectorsToday() {
    return client.get('news/sectors/today/')
  },
  // 카드뉴스 상세 (전문)
  cardNewsDetail(id) {
    return client.get(`news/sectors/card/${id}/`)
  },
  // 추천 화면 관심업종 종목 리스트 (백엔드 sectors/<id>/stocks/)
  sectorStocks(sectorId) {
    return client.get(`news/sectors/${sectorId}/stocks/`)
  },
}
