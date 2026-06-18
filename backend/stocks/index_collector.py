"""data.go.kr 금융위원회 지수시세정보 API로 코스피·코스닥 지수를 수집한다.

stocks/views.py:save_stocks의 requests/parse 패턴을 따른다.
※ 주식시세정보(getStockPriceInfo)와 별개 API이므로, 공공데이터포털에서
   '지수시세정보(GetMarketIndexInfoService)' 활용신청이 되어 있어야 호출된다.
"""

import requests
from datetime import datetime

from django.conf import settings

from .models import MarketIndexDaily

API_URL = "https://apis.data.go.kr/1160100/service/GetMarketIndexInfoService/getStockMarketIndex"

# 수집 대상 지수명(idxNm) — 정확히 일치하는 이름만 수집한다.
# 코스피·코스닥(전체 시장) + 코스피 200(대형주 코어) + KRX 300(통합 대표).
TARGET_INDICES = ("코스피", "코스닥", "코스피 200", "KRX 300")

# 최신 영업일을 안전하게 포함하도록 한 번에 가져오는 행 수(하루 약 140여 지수).
FETCH_ROWS = 500


def _parse_float(value):
	"""문자열 숫자를 float로 변환. 빈 값/오류는 None."""
	if value is None or value == "":
		return None
	try:
		return float(str(value).replace(",", ""))
	except ValueError:
		return None


def collect_indices():
	"""대상 지수들의 최신 지수를 수집해 MarketIndexDaily에 upsert한다.

	idxNm 부분일치 문제(예: '코스피'가 '코스피 200'까지 매칭)를 피하기 위해
	한 번 호출한 뒤 정확히 일치하는 이름만 최신 기준일(basDt) 기준으로 고른다.
	반환: 저장/갱신된 MarketIndexDaily 인스턴스 리스트.
	"""
	params = {
		"serviceKey": settings.FINANCIAL_API_KEY,
		"resultType": "json",
		"numOfRows": FETCH_ROWS,
		"pageNo": 1,
	}
	response = requests.get(API_URL, params=params)
	data = response.json()
	items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
	if isinstance(items, dict):       # 단건이면 dict로 올 수 있음
		items = [items]

	saved = []
	for index_name in TARGET_INDICES:
		# 정확히 일치하는 행만, 기준일이 가장 최신인 것을 선택.
		matches = [it for it in items if it.get("idxNm") == index_name and it.get("basDt")]
		if not matches:
			continue
		item = max(matches, key=lambda it: it["basDt"])

		close_price = _parse_float(item.get("clpr"))
		if close_price is None:
			continue
		try:
			base_date = datetime.strptime(item["basDt"], "%Y%m%d").date()
		except ValueError:
			continue

		obj, _ = MarketIndexDaily.objects.update_or_create(
			index_name=index_name,
			base_date=base_date,
			defaults={
				"close_price": close_price,
				"change": _parse_float(item.get("vs")) or 0.0,
				"change_rate": _parse_float(item.get("fltRt")) or 0.0,
			},
		)
		saved.append(obj)

	return saved
