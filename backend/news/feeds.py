"""경제 뉴스 RSS 피드 목록.

각 항목: (매체명, RSS URL). crawl_news 커맨드가 feedparser로 파싱한다.
URL이 변경/중단될 수 있으므로, 동작하지 않는 피드는 건너뛰고 로그를 남긴다.
"""

FEEDS = [
    ("연합뉴스", "https://www.yna.co.kr/rss/economy.xml"),
    ("매일경제", "https://www.mk.co.kr/rss/30100041/"),
    ("SBS Biz", "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02"),
]

# 최근 며칠치 기사만 수집/분석 대상으로 삼는다.
RECENT_DAYS = 2
