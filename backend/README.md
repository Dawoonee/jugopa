# Jugopa Backend

Django DRF 백엔드. 모든 명령은 이 `backend/` 디렉터리에서 실행합니다.

## 초기 세팅

```bash
# 1) 가상환경 활성화 후 의존성 설치
pip install -r requirements.txt

# 2) DB 마이그레이션
python manage.py migrate

# 3) 시드(콘텐츠) 데이터 적재 — 종목/시세/업종/뉴스/용어/퀴즈
python manage.py loaddata fixtures/seed_data.json

# 4) 개발 서버 실행
python manage.py runserver
```

> `db.sqlite3`는 git에 포함되지 않습니다(`.gitignore`). 위 `migrate` + `loaddata`로 동일한 콘텐츠 데이터를 갖춘 DB를 만들 수 있습니다. 사용자 계정·북마크·커뮤니티 글 등 **개인 데이터는 시드에 포함되지 않으므로** 각자 회원가입해서 사용하세요.

> **섹터 분류 체계**: 뉴스/카드뉴스는 WICS 기준 **중분류(28개)**, 마이페이지 관심 섹터는 **대분류(10개)** 로 동작합니다. 분류표는 루트의 `주식분류표.txt`를 따릅니다. `seed_data.json`에 새 체계가 포함되어 있으므로 **일반 팀원은 위 `loaddata`만으로 충분**합니다(아래 시드 커맨드는 관리자만 사용).

## 시드 데이터 갱신 (관리자용)

콘텐츠 데이터를 변경한 뒤 픽스처를 다시 만들어 커밋합니다. (Windows에서 `>` 리다이렉트는 인코딩 문제가 있으니 반드시 `-o` 옵션 사용)

### 섹터/뉴스 시드 재생성 순서

섹터 관련 데이터는 서로 의존성이 있어 **순서대로** 실행해야 합니다. `setup_sectors`가 1~2단계를 묶어 처리합니다.

```bash
# 1+2) 섹터 분류표(대10/중28) + 대표 종목 매핑 적재
#      (load_sectors → load_sector_stocks 순서로 실행. data.go.kr API 키 필요)
python manage.py setup_sectors
#      └ API 키 없이 섹터만 적재하려면: python manage.py setup_sectors --skip-stocks

# 3) 뉴스 RSS 수집 + 중분류 분류 + 카드뉴스 생성 (네트워크 + Anthropic API 키 필요)
python manage.py crawl_news
```

### 픽스처 덤프

```bash
python manage.py dumpdata \
  stocks.Stock stocks.StockPriceDaily stocks.DailyMarketWeather stocks.MarketIndexDaily \
  stocks.TrendKeyword stocks.StockKeyWordMapping \
  tutors.Term tutors.DailyTerm tutors.Quiz \
  news.Sector news.SectorStock news.NewsArticle news.SectorCardNews \
  --indent 2 -o fixtures/seed_data.json
```
