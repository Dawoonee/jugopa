import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Sector, SectorStock, SectorCardNews, NewsArticle
from stocks.models import Stock
from django.utils import timezone

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def large_sector():
    return Sector.objects.create(
        name="IT", level=Sector.Level.LARGE, display_order=1, is_active=True
    )

@pytest.fixture
def test_sector(large_sector):
    """카드뉴스/매핑 단위인 중분류(MID). 대분류 IT를 부모로 둔다."""
    return Sector.objects.create(
        name="반도체와 반도체장비", level=Sector.Level.MID,
        parent=large_sector, display_order=1, is_active=True,
    )

@pytest.fixture
def test_stock():
    return Stock.objects.create(stock_code="005930", stock_name="삼성전자", market_type="KOSPI")

@pytest.fixture
def test_sector_stock(test_sector, test_stock):
    return SectorStock.objects.create(sector=test_sector, stock=test_stock, rank=1)

@pytest.fixture
def test_card_news(test_sector):
    today = timezone.localdate()
    return SectorCardNews.objects.create(
        sector=test_sector,
        target_date=today,
        headline="IT News Headline",
        summary="IT Summary",
        rank=1
    )

@pytest.mark.django_db
class TestNewsAPI:
    def test_sectors_list_defaults_to_large(self, api_client, large_sector, test_sector):
        """관심 섹터 선택용 — 기본은 대분류(LARGE)만 반환한다."""
        url = reverse('news:sectors_list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        names = [s['name'] for s in response.data]
        assert "IT" in names                       # 대분류
        assert "반도체와 반도체장비" not in names    # 중분류는 제외

    def test_sectors_list_mid(self, api_client, large_sector, test_sector):
        url = reverse('news:sectors_list')
        response = api_client.get(url, {'level': 'MID'})
        assert response.status_code == status.HTTP_200_OK
        names = [s['name'] for s in response.data]
        assert "반도체와 반도체장비" in names
        assert "IT" not in names

    def test_sectors_today(self, api_client, test_card_news):
        url = reverse('news:sectors_today')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['headline'] == "IT News Headline"

    def test_card_news_detail(self, api_client, test_card_news):
        url = reverse('news:card_news_detail', kwargs={'card_id': test_card_news.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['headline'] == "IT News Headline"

    def test_sector_stocks(self, api_client, test_sector, test_sector_stock):
        url = reverse('news:sector_stocks', kwargs={'sector_id': test_sector.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['sector_id'] == test_sector.id
        assert len(response.data['stocks']) >= 1
        assert response.data['stocks'][0]['stock_code'] == "005930"

    def test_sector_stocks_large_aggregates_children(
        self, api_client, large_sector, test_sector, test_sector_stock
    ):
        """대분류 id로 조회하면 자식 중분류들의 매핑을 집계해 반환한다."""
        url = reverse('news:sector_stocks', kwargs={'sector_id': large_sector.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        codes = [s['stock_code'] for s in response.data['stocks']]
        assert "005930" in codes

    def test_sector_breakdown_large_groups_by_children(
        self, api_client, large_sector, test_sector, test_sector_stock
    ):
        """대분류 id로 조회하면 자식 중분류별 그룹 트리를 반환한다."""
        url = reverse('news:sector_breakdown', kwargs={'sector_id': large_sector.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['level'] == 'LARGE'
        assert response.data['total_count'] == 1
        group_names = [g['sector_name'] for g in response.data['groups']]
        assert "반도체와 반도체장비" in group_names
        semi = next(g for g in response.data['groups'] if g['sector_name'] == "반도체와 반도체장비")
        assert semi['stock_count'] == 1
        assert semi['stocks'][0]['stock_code'] == "005930"

    def test_sector_breakdown_mid_single_group(
        self, api_client, test_sector, test_sector_stock
    ):
        """중분류 id로 조회하면 자기 자신 1개 그룹만 반환한다."""
        url = reverse('news:sector_breakdown', kwargs={'sector_id': test_sector.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['level'] == 'MID'
        assert len(response.data['groups']) == 1
        assert response.data['groups'][0]['sector_id'] == test_sector.id
        assert response.data['groups'][0]['stocks'][0]['stock_code'] == "005930"


@pytest.mark.django_db
class TestLoadSectors:
    def test_load_sectors_seeds_hierarchy(self):
        from django.core.management import call_command
        call_command('load_sectors')

        assert Sector.objects.filter(level=Sector.Level.LARGE).count() == 10
        assert Sector.objects.filter(level=Sector.Level.MID).count() == 28
        # 모든 중분류는 대분류 부모를 가진다
        orphan_mid = Sector.objects.filter(
            level=Sector.Level.MID, parent__isnull=True
        ).count()
        assert orphan_mid == 0


class TestNaverSectorMap:
    def test_all_targets_are_valid_mid_sectors(self):
        """NAVER_TO_WICS의 모든 값은 sectors_seed의 중분류명과 일치해야 한다."""
        from news.naver_sector_map import NAVER_TO_WICS
        from news.sectors_seed import MID_SECTORS

        valid_mids = {
            mid_name
            for mids in MID_SECTORS.values()
            for mid_name, _keywords in mids
        }
        invalid = {v for v in NAVER_TO_WICS.values() if v not in valid_mids}
        assert not invalid, f"중분류명과 불일치하는 매핑 값: {invalid}"

    def test_map_naver_to_wics(self):
        from news.naver_sector_map import map_naver_to_wics
        assert map_naver_to_wics("반도체와반도체장비") == "반도체와 반도체장비"
        assert map_naver_to_wics("자동차부품") == "자동차와 부품"
        assert map_naver_to_wics(" 은행 ") == "은행"   # 공백 보정
        assert map_naver_to_wics("기타") is None
        assert map_naver_to_wics(None) is None


@pytest.mark.django_db
class TestLoadAllSectorStocks:
    def _mock_fetchers(self, monkeypatch):
        """네이버/FDR 페처를 대체한다. 888888는 업종 미매핑('기타'), 777777은 시세 누락."""
        from stocks import sector_universe

        def fake_listing(markets=None):
            return {
                "005930": {"name": "삼성전자", "market": "KOSPI", "marcap": 400_000_000_000_000,
                           "close": 71000, "open": 70000, "high": 72000, "low": 69000, "volume": 1000},
                "000270": {"name": "기아", "market": "KOSPI", "marcap": 30_000_000_000_000,
                           "close": 90000, "open": 89000, "high": 91000, "low": 88000, "volume": 500},
                "035720": {"name": "카카오", "market": "KOSPI", "marcap": 20_000_000_000_000,
                           "close": 40000, "open": 39000, "high": 41000, "low": 39000, "volume": 800},
                "888888": {"name": "기타종목", "market": "KOSDAQ", "marcap": 1_000_000,
                           "close": 100, "open": 100, "high": 100, "low": 100, "volume": 1},
            }

        def fake_membership():
            return {
                "005930": "반도체와반도체장비",
                "000270": "자동차부품",
                "035720": "양방향미디어와서비스",
                "888888": "기타",          # 미매핑 → 적재 제외
                "777777": "은행",          # listing에 없음 → 적재 제외
            }

        monkeypatch.setattr(sector_universe, 'fetch_listing', fake_listing)
        monkeypatch.setattr(sector_universe, 'fetch_sector_membership', fake_membership)

    def test_classifies_and_persists(self, monkeypatch):
        from django.core.management import call_command
        call_command('load_sectors')
        self._mock_fetchers(monkeypatch)

        call_command('load_all_sector_stocks')

        assert Stock.objects.get(stock_code="005930").sector_links.get().sector.name == "반도체와 반도체장비"
        assert Stock.objects.get(stock_code="000270").sector_links.get().sector.name == "자동차와 부품"
        assert Stock.objects.get(stock_code="035720").sector_links.get().sector.name == "미디어와 엔터테인먼트"
        # 시총·시세도 적재된다
        samsung = Stock.objects.get(stock_code="005930")
        assert samsung.market_cap == 400_000_000_000_000
        assert samsung.daily_prices.count() == 1
        # 미매핑('기타') / 시세 누락 종목은 적재되지 않는다
        assert not Stock.objects.filter(stock_code="888888").exists()
        assert not Stock.objects.filter(stock_code="777777").exists()

    def test_dry_run_does_not_persist(self, monkeypatch):
        from django.core.management import call_command
        call_command('load_sectors')
        self._mock_fetchers(monkeypatch)

        call_command('load_all_sector_stocks', '--dry-run')

        assert SectorStock.objects.count() == 0
        assert Stock.objects.count() == 0

    def test_requires_sectors_loaded(self, monkeypatch):
        from django.core.management import call_command
        self._mock_fetchers(monkeypatch)
        # load_sectors 미실행 → 적재 없이 종료
        call_command('load_all_sector_stocks')
        assert SectorStock.objects.count() == 0
