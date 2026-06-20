import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Stock, StockPriceDaily, MarketIndexDaily, DailyMarketWeather, UserBookmark

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    return User.objects.create_user(username="testuser", password="testpassword123", nickname="tester")

@pytest.fixture
def test_stock():
    return Stock.objects.create(stock_code="005930", stock_name="삼성전자", market_type="KOSPI")

@pytest.fixture
def test_stock_price(test_stock):
    today = timezone.localdate()
    return StockPriceDaily.objects.create(
        stock=test_stock,
        record_date=today,
        open_price=80000,
        close_price=82000,
        high_price=83000,
        low_price=79000,
        volume=1000000
    )

@pytest.mark.django_db
class TestStocksAPI:

    @patch('stocks.views.requests.get')
    def test_save_stocks(self, mock_get, api_client):
        # Mock the external API response
        mock_get.return_value.json.return_value = {
            "response": {
                "body": {
                    "items": {
                        "item": [
                            {
                                "srtnCd": "000660",
                                "itmsNm": "SK하이닉스",
                                "mrktCtg": "KOSPI",
                                "basDt": "20231010",
                                "mkp": "120000",
                                "clpr": "125000",
                                "hipr": "126000",
                                "lopr": "119000",
                                "trqu": "500000"
                            }
                        ]
                    }
                }
            }
        }
        url = reverse('stocks:save_stocks')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_201_CREATED
        assert Stock.objects.filter(stock_code="000660").exists()

    def test_stock_list_create_get(self, api_client, test_stock):
        url = reverse('stocks:stock_list_create')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    @patch('stocks.views.fetch_stock_by_name')
    def test_stock_search(self, mock_fetch, api_client, test_stock):
        # 1. Search existing stock
        url = reverse('stocks:stock_search')
        response = api_client.get(url, {'q': '삼성전자'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['stock_code'] == "005930"

        # 2. Search new stock (triggers fallback)
        def create_naver_stock(query):
            return Stock.objects.create(stock_code="035420", stock_name="NAVER", market_type="KOSPI")
        mock_fetch.side_effect = create_naver_stock
        response = api_client.get(url, {'q': 'NAVER'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['stock_code'] == "035420"
        mock_fetch.assert_called_once_with("NAVER")

    @patch('stocks.views.fetch_price_history')
    def test_stock_detail(self, mock_fetch_history, api_client, test_stock, test_stock_price):
        url = reverse('stocks:stock_detail', kwargs={'stock_code': test_stock.stock_code})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['stock_code'] == "005930"
        # The mock will be called if there are not enough daily prices (PRICE_FRESHNESS_MIN_COUNT=20)
        # Since we only created 1, it should be called.
        mock_fetch_history.assert_called_once()

    def test_bookmarks_get(self, api_client, test_user, test_stock):
        api_client.force_authenticate(user=test_user)
        UserBookmark.objects.create(user=test_user, stock=test_stock)
        url = reverse('stocks:bookmarks')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['stock_code'] == "005930"

    def test_bookmarks_post(self, api_client, test_user, test_stock):
        api_client.force_authenticate(user=test_user)
        url = reverse('stocks:bookmarks')
        data = {"stock_code": test_stock.stock_code}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert UserBookmark.objects.filter(user=test_user, stock=test_stock).exists()

    def test_bookmark_delete(self, api_client, test_user, test_stock):
        api_client.force_authenticate(user=test_user)
        UserBookmark.objects.create(user=test_user, stock=test_stock)
        url = reverse('stocks:bookmark_delete', kwargs={'stock_code': test_stock.stock_code})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not UserBookmark.objects.filter(user=test_user, stock=test_stock).exists()

    def test_market_indices(self, api_client):
        today = timezone.localdate()
        MarketIndexDaily.objects.create(
            index_name="코스피", base_date=today, close_price=2500.0, change=10.0, change_rate=0.4
        )
        url = reverse('stocks:market_indices')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_market_weather_today(self, api_client):
        today = timezone.localdate()
        DailyMarketWeather.objects.create(
            target_date=today, weather_status="SUNNY", message="Good day"
        )
        url = reverse('stocks:market_weather_today')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['weather_status'] == "SUNNY"

    def test_top_performer(self, api_client, test_stock_price):
        url = reverse('stocks:top_performer')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['stock_code'] == test_stock_price.stock.stock_code
