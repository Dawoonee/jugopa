"""종목명으로 data.go.kr 주식시세정보 API를 조회해 Stock·시세를 적재한다.

섹터별 대표 종목을 동적으로 확보하기 위해 사용한다(load_sector_stocks).
save_stocks 뷰와 동일한 getStockPriceInfo API를 쓰되, likeItmsNm(종목명 검색)으로 호출한다.
"""

import requests
from datetime import datetime, timedelta

from django.conf import settings

from .models import Stock, StockPriceDaily

API_URL = "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"


def _parse_int(value):
	if value is None or value == "":
		return -1
	try:
		return int(value)
	except ValueError:
		return -1


def fetch_stock_by_name(name):
	"""종목명으로 최신 시세를 조회해 Stock + StockPriceDaily를 upsert하고 Stock을 반환한다.

	정확히 일치하는 종목명을 우선하고, 최신 기준일(basDt) 행을 사용한다.
	조회 실패 시 None.
	"""
	params = {
		"serviceKey": settings.FINANCIAL_API_KEY,
		"resultType": "json",
		"numOfRows": 10,
		"pageNo": 1,
		"likeItmsNm": name,
	}
	try:
		response = requests.get(API_URL, params=params, timeout=30)
		data = response.json()
	except Exception:
		return None

	items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
	if isinstance(items, dict):
		items = [items]
	if not items:
		return None

	# 정확히 일치하는 종목명 우선, 없으면 전체 후보. 그중 최신 기준일 선택.
	exact = [it for it in items if it.get("itmsNm") == name]
	candidates = exact or items
	item = max(candidates, key=lambda it: it.get("basDt", ""))

	stock_code = item.get("srtnCd")
	if not stock_code:
		return None

	stock, _ = Stock.objects.update_or_create(
		stock_code=stock_code,
		defaults={
			"stock_name": item.get("itmsNm", name),
			"market_type": item.get("mrktCtg", ""),
			"market_cap": _parse_int(item.get("mrktTotAmt", "0")),
		},
	)

	bas_dt = item.get("basDt")
	if bas_dt:
		try:
			record_date = datetime.strptime(bas_dt, "%Y%m%d").date()
			StockPriceDaily.objects.update_or_create(
				stock=stock,
				record_date=record_date,
				defaults={
					"open_price": _parse_int(item.get("mkp")),
					"close_price": _parse_int(item.get("clpr")),
					"high_price": _parse_int(item.get("hipr")),
					"low_price": _parse_int(item.get("lopr")),
					"volume": _parse_int(item.get("trqu")),
				},
			)
		except ValueError:
			pass

	return stock


def fetch_price_history(stock_code, days=30):
	"""종목코드로 최근 days(영업일) 시세를 조회해 StockPriceDaily를 upsert하고 적재 건수를 반환한다.

	공공API getStockPriceInfo를 likeSrtnCd(종목코드) + 기준일 범위로 호출한다.
	주말·공휴일을 감안해 넉넉히 days*2일 전부터 조회하고, srtnCd가 정확히 일치하는 행만 적재한다.
	"""
	stock = Stock.objects.filter(stock_code=stock_code).first()
	if not stock:
		return 0

	end_dt = datetime.now().date()
	begin_dt = end_dt - timedelta(days=days * 2)
	params = {
		"serviceKey": settings.FINANCIAL_API_KEY,
		"resultType": "json",
		"numOfRows": days * 2,
		"pageNo": 1,
		"likeSrtnCd": stock_code,
		"beginBasDt": begin_dt.strftime("%Y%m%d"),
		"endBasDt": end_dt.strftime("%Y%m%d"),
	}
	try:
		response = requests.get(API_URL, params=params, timeout=30)
		data = response.json()
	except Exception:
		return 0

	items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
	if isinstance(items, dict):
		items = [items]

	saved = 0
	# items는 내림차순(최신순) 정렬되어 있음
	for i, item in enumerate(items):
		# likeSrtnCd는 부분일치이므로 정확히 일치하는 종목만 적재한다.
		if item.get("srtnCd") != stock_code:
			continue
		
		# 가장 최신 기준일(첫 번째 아이템)의 시가총액으로 Stock 갱신
		if i == 0 and "mrktTotAmt" in item:
			stock.market_cap = _parse_int(item.get("mrktTotAmt", "0"))
			stock.save()

		bas_dt = item.get("basDt")
		if not bas_dt:
			continue
		try:
			record_date = datetime.strptime(bas_dt, "%Y%m%d").date()
		except ValueError:
			continue
		StockPriceDaily.objects.update_or_create(
			stock=stock,
			record_date=record_date,
			defaults={
				"open_price": _parse_int(item.get("mkp")),
				"close_price": _parse_int(item.get("clpr")),
				"high_price": _parse_int(item.get("hipr")),
				"low_price": _parse_int(item.get("lopr")),
				"volume": _parse_int(item.get("trqu")),
			},
		)
		saved += 1

	return saved
