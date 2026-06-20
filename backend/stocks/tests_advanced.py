import pytest

@pytest.mark.django_db
class TestAdvancedStocksAPI:
    def test_stock_categorization(self):
        """
        TODO: 주식 분류(대분류, 중분류) 적용 여부 검증
        - 주식 조회 시 해당 카테고리 응답 포함 여부 확인
        """
        pytest.skip("주식 분류 기능 개발 후 테스트 로직 작성")
