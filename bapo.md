# Jugopa 배포 가이드 (Supabase + Render + Vercel)

> 아키텍처
> - **프론트엔드(Vue SPA)** → Vercel
> - **DB(Postgres)** → Supabase
> - **미디어(프로필 이미지)** → Supabase Storage (S3 호환)
> - **백엔드(Django + Gunicorn)** → Render Web Service
> - **일배치(daily_update, crawl_news)** → Render Cron Job

시드는 무거운 LLM/API 커맨드를 다시 돌릴 필요 없이 이미 커밋된
`backend/fixtures/seed_data.json`(약 4.5MB, 종목·섹터·용어·퀴즈·뉴스·카드뉴스 전체 포함,
**유저 데이터 없음**)을 `loaddata` 한 번으로 적재합니다.

---

## 1️⃣ Supabase — DB + Storage

### 1-A. 프로젝트 생성
1. https://supabase.com → **New project**
2. Region은 **Northeast Asia (Seoul) `ap-northeast-2`** 선택 (지연 최소)
3. Database Password를 강하게 설정하고 **따로 저장** (이게 `DATABASE_URL`에 들어감)

### 1-B. DATABASE_URL 확보
1. **Project Settings → Database → Connection string**
2. **⚠️ "Session pooler"** 탭을 선택 (Direct connection은 IPv6 전용이라 Render에서 연결 실패할 수 있음).
   Session pooler는 IPv4 + 영속 연결 + 마이그레이션 모두 지원.
3. 형식:
   ```
   postgresql://postgres.<project-ref>:<password>@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres
   ```
   → 이 값이 Render의 `DATABASE_URL`

### 1-C. Storage 버킷
1. **Storage → New bucket** → 이름 `media`, **Public bucket 체크**
   (프로필 이미지가 브라우저에서 직접 로드돼야 하므로)
2. **Storage → S3 connection** (또는 Settings → Storage)에서:
   - **Endpoint** 복사: `https://<project-ref>.supabase.co/storage/v1/s3` → `AWS_S3_ENDPOINT_URL`
   - **Region**: `ap-northeast-2` → `AWS_S3_REGION_NAME`
3. **S3 Access Keys → New access key** 생성 → `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
   (한 번만 보임, 저장)

> ⚠️ **이미지 URL 주의(중요):** Supabase의 public 객체 URL은 `/storage/v1/object/public/...` 경로인데,
> django-storages 기본값은 S3 endpoint(`/s3/...`) 경로로 URL을 만들어 **브라우저에서 이미지가 안 뜸.**
> 이걸 맞추려면 settings에 `AWS_S3_CUSTOM_DOMAIN = "<ref>.supabase.co/storage/v1/object/public/media"`
> 한 줄을 추가해야 함 (코드 수정 필요 — 아래 마지막 항목 참고).

---

## 2️⃣ Render — 백엔드

### 2-A. Blueprint 배포
1. 변경사항을 GitHub에 푸시 (`render.yaml`이 repo 루트에 있어야 함)
2. https://render.com → **New → Blueprint** → 이 레포 연결 → `render.yaml` 자동 인식
3. web 1개 + cron 2개 + Environment Group 1개가 생성됨

### 2-B. 환경변수 입력 (대시보드)
`render.yaml`에서 `sync: false`로 둔 값들을 직접 채움.
**web 서비스**와 **Environment Group(`jugopa-backend-env`, cron들이 공유)** 둘 다 동일하게:

| 키 | 값 출처 / 예시 |
|---|---|
| `DATABASE_URL` | 1-B의 Session pooler URI |
| `ALLOWED_HOSTS` | `jugopa-backend.onrender.com` (배포 후 받는 실제 Render 도메인) |
| `CSRF_TRUSTED_ORIGINS` | `https://jugopa-backend.onrender.com,https://<your>.vercel.app` |
| `CORS_ALLOWED_ORIGINS` | `https://<your>.vercel.app` (4단계에서 받는 Vercel 도메인) |
| `FINANCIAL_API_KEY` | 기존 `.env` 값 |
| `GMS_API_KEY` / `GMS_API_KEY2` | 기존 `.env` 값 |
| `GMS_BASE_URL` / `GMS_BASE_URL2` | `https://gms.ssafy.io/gmsapi/api.openai.com/v1` |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | 1-C 발급값 |
| `AWS_STORAGE_BUCKET_NAME` | `media` |
| `AWS_S3_ENDPOINT_URL` | 1-C endpoint |
| `AWS_S3_REGION_NAME` | `ap-northeast-2` |

> `SECRET_KEY`는 `generateValue: true`라 Render가 자동 생성. `DEBUG=False`, `USE_S3=True`는 yaml에 고정.
>
> **닭-달걀 문제:** Render 도메인은 배포돼야 정해지고, Vercel 도메인은 4단계에서 정해짐.
> 일단 임시로 채워 배포 → 도메인 확정 후 `ALLOWED_HOSTS`/`CORS_ALLOWED_ORIGINS`를 다시 채우고
> 재배포(저장 시 자동 재배포)하면 됨.

### 2-C. 배포 흐름
- build 시 `collectstatic` → preDeploy 시 `migrate`(자동) → `gunicorn` 기동
- 첫 배포 후 web 서비스의 실제 URL 확인 → `ALLOWED_HOSTS` 등에 반영

### 2-D. 시드 데이터 적재 (마이그레이션 후 1회)
Render **web 서비스 → Shell** 탭에서:
```bash
python manage.py loaddata fixtures/seed_data.json
```
이거 하나로 종목/섹터/용어/퀴즈/뉴스/카드뉴스가 모두 들어감. (LLM·API 재호출 불필요)

> 그 후의 일일 갱신은 cron(`daily_update` 01:30 UTC, `crawl_news` 00:00 UTC)이 자동 처리.

---

## 3️⃣ Render RAM 결정 (cron)
`daily_update`/`generate_positive_cardnews`가 `torch` + KR-FinBert로 감성 추론을 수행.
Render Free/Starter(512MB)는 **OOM(메모리 부족)으로 죽을 수 있음.**
- `jugopa-daily-update` cron은 **Standard(2GB)** 이상 권장 (yaml에 이미 `plan: standard`)
- web과 crawl_news는 추론을 안 하므로 더 작은 티어로 시작 가능

---

## 4️⃣ Vercel — 프론트엔드
1. https://vercel.com → **Add New → Project** → 레포 import
2. **Root Directory = `frontend`** 로 설정 (모노레포라 필수)
3. Framework은 Vite 자동 감지 / Build `npm run build` / Output `dist` (vercel.json에 명시됨)
4. **Settings → Environment Variables**:
   - `VITE_API_BASE_URL` = `https://jugopa-backend.onrender.com/api/v1`
     (2단계 Render 도메인 + `/api/v1`)
5. Deploy → Vercel 도메인(`https://<your>.vercel.app`) 확인
6. **이 도메인을 2-B의 `CORS_ALLOWED_ORIGINS`/`CSRF_TRUSTED_ORIGINS`에 넣고 Render 재배포**

---

## 5️⃣ 배포 후 검증 체크리스트
1. **백엔드**: `https://<render>/api/v1/` 접속, Render 로그에 OOM/누락 env 없는지
2. **DB**: Supabase Table Editor에 마이그레이션 + 시드 데이터 보이는지
3. **CORS**: Vercel 사이트에서 로그인/조회 시 콘솔에 CORS 에러 없는지
4. **토큰 리프레시**: 로그인 후 시간 지나도 자동 재발급되는지
5. **이미지**: 프로필 이미지 업로드 → Supabase `media` 버킷에 객체 생성 + 화면에 표시되는지
   (위 1-C 경고 해결 필요)
6. **cron**: Render cron `daily_update` 수동 트리거 → 완료 + 메모리 여유
7. **SPA 라우팅**: `/recommend` 직접 접속/새로고침 시 404 안 나는지

---

## 6️⃣ 남은 코드 수정 (이미지 표시용)
이미지가 실제로 표시되려면 **1-C의 `AWS_S3_CUSTOM_DOMAIN` 설정이 코드에 필요**(현재 settings엔 없음).
- `backend/config/settings.py`: `AWS_S3_CUSTOM_DOMAIN`을 환경변수로 추가
- `render.yaml` / `backend/.env.example`: 해당 키 추가
- 값 예시: `<project-ref>.supabase.co/storage/v1/object/public/media`

---

## 부록: 이번 배포 준비로 변경된 파일
**백엔드**
- `backend/config/settings.py` — DATABASE_URL/ALLOWED_HOSTS/CORS/CSRF 환경변수화, corsheaders 배선,
  WhiteNoise 정적, USE_S3 Supabase Storage, 운영 보안 토글, DRF 인증 중복 제거
- `backend/requirements.txt` — gunicorn, psycopg[binary], whitenoise[brotli], django-storages, boto3
- `render.yaml` (신규) — web + cron 2개 + Environment Group
- `backend/.env.example` (신규)

**프론트엔드**
- `frontend/src/api/client.js` — VITE_API_BASE_URL 환경변수화 + 토큰 리프레시 절대경로 버그 수정
- `frontend/vercel.json`, `frontend/.env.production`, `frontend/.env.example` (신규)
