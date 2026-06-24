"""
Django settings for config project.
"""

from pathlib import Path
import os
import environ

# 1. BASE_DIR 설정 (최상단)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. environ 초기화 및 .env 파일 읽기
env = environ.Env(
    DEBUG=(bool, False)
)
# BASE_DIR 경로에 있는 .env 파일을 읽어옵니다.
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# 3. 환경변수 적용
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
FINANCIAL_API_KEY = env('FINANCIAL_API_KEY')

# GMS (챗봇용 LLM, OpenAI 호환 API)
GMS_API_KEY = env('GMS_API_KEY', default='')
GMS_BASE_URL = env('GMS_BASE_URL', default='')
GMS_MODEL = env('GMS_MODEL', default='gpt-5-nano')

# GMS (news 카드뉴스 요약용 — 챗봇과 별도 키). 미설정 시 챗봇 설정으로 폴백.
GMS_API_KEY2 = env('GMS_API_KEY2', default=GMS_API_KEY)
GMS_BASE_URL2 = env('GMS_BASE_URL2', default=GMS_BASE_URL)
GMS_MODEL2 = env('GMS_MODEL2', default=GMS_MODEL)

# 운영 호스트/오리진 (콤마 구분, 미설정 시 로컬 기본값)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# Application definition
INSTALLED_APPS = [
    # Local Apps (생성한 앱들)
    'accounts',
    'stocks',
    'tutors',
    'community',
    'news',
    'chatbot',

    # 3rd Party Apps (DRF 등 외부 라이브러리)
    'rest_framework',
    'corsheaders',

    # Django Default Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # 필요시 [BASE_DIR / 'templates'] 등으로 추가 가능
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# DATABASE_URL 미설정 시 로컬 SQLite 로 폴백 (운영: Supabase Postgres URI)
DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
# 한국 시간 및 언어로 설정하시는 것을 추천합니다.
LANGUAGE_CODE = 'ko-kr' 
TIME_ZONE = 'Asia/Seoul' 

USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (사용자 업로드 — 프로필 이미지 등)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 스토리지 백엔드
# - USE_S3=True(운영): 미디어는 Supabase Storage(S3 호환), 정적은 WhiteNoise
# - 그 외(로컬 개발): 미디어는 파일시스템, 정적은 Django 기본
USE_S3 = env.bool('USE_S3', default=False)

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

if not DEBUG:
    STORAGES['staticfiles']['BACKEND'] = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

if USE_S3:
    # Supabase Storage (S3 호환) 자격증명 — 모두 환경변수로 주입
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL')  # 예: https://<project>.supabase.co/storage/v1/s3
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_ADDRESSING_STYLE = 'path'  # Supabase 권장
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN")
    STORAGES['default']['BACKEND'] = 'storages.backends.s3.S3Storage'

# 프로덕션 보안 설정 (운영에서 DEBUG=False)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model 설정 (필수!)
AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication', # JWT 사용 시
        'rest_framework.authentication.SessionAuthentication',
    ],
}