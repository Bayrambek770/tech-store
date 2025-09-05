from pathlib import Path
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent
try:
    from decouple import config
except ImportError:
    def config(key, default=None, cast=str):
        return default

def bool_env(name, default=False):
    return config(name, default=str(default)).lower() in ('1', 'true', 'yes', 'on')

def list_env(name, default=""):
    raw = config(name, default=default)
    return [p.strip() for p in raw.split(',') if p.strip()]

SECRET_KEY = config('DJANGO_SECRET_KEY', default='CHANGE_ME_IN_PRODUCTION')
DEBUG = bool_env('DJANGO_DEBUG', False)
ALLOWED_HOSTS = list_env('DJANGO_ALLOWED_HOSTS', '*') or ['*']
CSRF_TRUSTED_ORIGINS = list_env('DJANGO_CSRF_TRUSTED_ORIGINS', '')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'parler',
    
    # local_apps
    'products',
    'users',
    'designs',
    'orders',
    'payment',
    # 'rosetta',  # disabled
    'rest_framework',
]

AUTH_USER_MODEL = "users.CustomUser"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
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
        'DIRS': [
            BASE_DIR / 'templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


DB_ENGINE = config('DB_ENGINE', default='django.db.backends.sqlite3')
DB_NAME = config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3'))

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': DB_NAME,
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}


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


LANGUAGE_CODE = config('LANGUAGE_CODE', default='ru')

LANGUAGES = [
    ('ru', _('Russian')),
    ('en', _('English')),
    ('uz', _('Uzbek')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale'
]


LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 30

TIME_ZONE = config('TIME_ZONE', default='UTC')

USE_I18N = True

USE_TZ = True


STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'assets']
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER or 'webmaster@localhost')

PAYLOV_MERCHANT_ID = config("PAYLOV_MERCHANT_ID", "")
PAYLOV_USERNAME = config("PAYLOV_USERNAME", "")
PAYLOV_PASSWORD = config("PAYLOV_PASSWORD", "")
PAYLOV_FORCE_TIYIN = bool_env('PAYLOV_FORCE_TIYIN', False)

# Base site URL (needed for external payment return links)
# If not provided via env SITE_BASE_URL, derive a sensible default.
SITE_BASE_URL = config('SITE_BASE_URL', default=('http://localhost:8000' if DEBUG else (ALLOWED_HOSTS[0].rstrip('/') if ALLOWED_HOSTS and ALLOWED_HOSTS[0] != '*' else ''))) or ''

# Currency configuration (basic two-currency support for checkout)
SUPPORTED_CURRENCIES = ['UZS', 'USD']
DEFAULT_DISPLAY_CURRENCY = 'UZS'
# django-parler configuration
PARLER_LANGUAGES = {
    None: (
        {'code': 'ru'},
        {'code': 'en'},
        {'code': 'uz'},
    ),
    'default': {
        'fallbacks': ['ru'],
        'hide_untranslated': False,
    }
}

# ------------------------------------------------------------------
# Security hardening (only effective when DEBUG=False)
# ------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

LOG_LEVEL = config('DJANGO_LOG_LEVEL', default='INFO')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[{levelname}] {asctime} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
}


try:
    from .local_settings import *
except ImportError:
    pass
