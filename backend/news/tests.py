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
def test_sector():
    return Sector.objects.create(name="IT", display_order=1, is_active=True)

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
    def test_sectors_list(self, api_client, test_sector):
        url = reverse('news:sectors_list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]['name'] == "IT"

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
