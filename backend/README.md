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

## 시드 데이터 갱신 (관리자용)

콘텐츠 데이터를 변경한 뒤 픽스처를 다시 만들어 커밋합니다. (Windows에서 `>` 리다이렉트는 인코딩 문제가 있으니 반드시 `-o` 옵션 사용)

```bash
python manage.py dumpdata \
  stocks.Stock stocks.StockPriceDaily stocks.DailyMarketWeather stocks.MarketIndexDaily \
  stocks.TrendKeyword stocks.StockKeyWordMapping \
  tutors.Term tutors.DailyTerm tutors.Quiz \
  news.Sector news.SectorStock news.NewsArticle news.SectorCardNews \
  --indent 2 -o fixtures/seed_data.json
```
