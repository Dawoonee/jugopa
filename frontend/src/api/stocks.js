import client from './client'

export const stocksApi = {
  indices() {
    return client.get('stocks/indices/')
  },
  weatherToday() {
    return client.get('stocks/weather/today/')
  },
  list() {
    return client.get('stocks/')
  },
  detail(code) {
    return client.get(`stocks/${code}/`)
  },
  search(q) {
    return client.get('stocks/search/', { params: { q } })
  },
  bookmarks() {
    return client.get('stocks/bookmarks/')
  },
  addBookmark(stockCode) {
    return client.post('stocks/bookmarks/', { stock_code: stockCode })
  },
  removeBookmark(stockCode) {
    return client.delete(`stocks/bookmarks/${stockCode}/`)
  },
}
