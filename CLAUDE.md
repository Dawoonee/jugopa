# Project: Jugopa

## Stack
- Backend: Python 3.x, Django DRF, PostgreSQL + PostGIS
- Frontend: Vue 3 (SPA), Leaflet, 워드클라우드
- Pipeline: n8n
- IDE: VSCode

## Backend Rules (Python/Django)
- PEP 8 + Black 포맷터
- 들여쓰기: 탭(\t) 사용, indent depth 최대 2
- 명명: snake_case(변수/함수), PascalCase(클래스), UPPER_SNAKE_CASE(상수)
- 최대 줄 길이: 120자
- 함수는 단일 책임 원칙 — 작게 유지
- 테스트: pytest, pytest-django

## Frontend Rules (Vue 3)
- Prettier + ESLint
- 명명: camelCase(변수/함수), PascalCase.vue(컴포넌트), kebab-case(CSS)

## DB Rules
- 테이블/컬럼: snake_case
- 공간 컬럼명: geom, geography 명시
- PostGIS 빈번 연산 컬럼: GIST 인덱스 필수

## Git Convention
# 브랜치: 태그/#이슈번호-기능명 (예: feat/#12-stock-chart)
c# 커밋: {이모지} {태그}: [{기능명}] 메시지 (#이슈번호)
# PR 제목: 🔀 merge: [날짜] 이름 한일 종료여부