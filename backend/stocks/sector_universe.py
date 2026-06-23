"""상장 전 종목 유니버스(시세·시총)와 네이버 업종 분류를 수집한다.

- fetch_listing(): FinanceDataReader로 KRX 상장 전 종목의 시세/시가총액을 한 번에 받는다.
- fetch_sector_membership(): 네이버 금융 '업종분류'를 스크래핑해 종목→업종 맵을 만든다.

둘 다 네트워크에 의존하므로 함수 단위로 분리해 load_all_sector_stocks 커맨드와 테스트(mock)가 쓴다.
pykrx는 KRX OTP 차단 환경에서 빈 응답을 주는 일이 잦아 이 두 소스로 대체했다.
"""

import re

import requests
from bs4 import BeautifulSoup

MARKETS = ("KOSPI", "KOSDAQ")
NAVER_LIST_URL = "https://finance.naver.com/sise/sise_group.naver?type=upjong"
NAVER_DETAIL_URL = "https://finance.naver.com/sise/sise_group_detail.naver?type=upjong&no={no}"
HEADERS = {"User-Agent": "Mozilla/5.0"}
_CODE_RE = re.compile(r"code=(\d{6})")


def _to_int(value):
	try:
		if value is None:
			return 0
		return int(value)
	except (TypeError, ValueError):
		return 0


def fetch_listing(markets=MARKETS):
	"""FDR로 `{종목코드: {name, market, marcap, close, open, high, low, volume}}`를 반환한다."""
	import FinanceDataReader as fdr

	df = fdr.StockListing("KRX")
	allowed = set(markets)
	listing = {}
	for row in df.itertuples(index=False):
		market = getattr(row, "Market", "")
		if market not in allowed:
			continue
		code = getattr(row, "Code", None)
		if not code:
			continue
		listing[code] = {
			"name": getattr(row, "Name", ""),
			"market": market,
			"marcap": _to_int(getattr(row, "Marcap", 0)),
			"close": _to_int(getattr(row, "Close", 0)),
			"open": _to_int(getattr(row, "Open", 0)),
			"high": _to_int(getattr(row, "High", 0)),
			"low": _to_int(getattr(row, "Low", 0)),
			"volume": _to_int(getattr(row, "Volume", 0)),
		}
	return listing


def _fetch_industry_list(session):
	"""(no, 업종명) 목록을 반환한다."""
	resp = session.get(NAVER_LIST_URL, timeout=15)
	resp.encoding = "euc-kr"
	soup = BeautifulSoup(resp.text, "html.parser")
	industries = []
	for a in soup.select("table.type_1 a[href*='sise_group_detail']"):
		name = a.get_text(strip=True)
		href = a.get("href", "")
		if name and "no=" in href:
			no = href.split("no=")[1].split("&")[0]
			industries.append((no, name))
	return industries


def _fetch_industry_codes(session, no):
	"""업종 상세 페이지의 구성종목 코드 리스트를 반환한다."""
	resp = session.get(NAVER_DETAIL_URL.format(no=no), timeout=15)
	resp.encoding = "euc-kr"
	soup = BeautifulSoup(resp.text, "html.parser")
	codes = []
	for link in soup.select("table.type_5 a[href*='/item/main']"):
		m = _CODE_RE.search(link.get("href", ""))
		if m:
			codes.append(m.group(1))
	return codes


def fetch_sector_membership():
	"""네이버 업종분류를 스크래핑해 `{종목코드: 네이버업종명}`을 반환한다."""
	session = requests.Session()
	session.headers.update(HEADERS)
	membership = {}
	for no, industry in _fetch_industry_list(session):
		for code in _fetch_industry_codes(session, no):
			membership[code] = industry
	return membership
