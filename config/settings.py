from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------
# Environment configuration via django-decouple
# ------------------------------------------------------------------
try:
    from decouple import config, Csv
except ModuleNotFoundError:  # fallback if decouple not installed
    def config(key, default=None, cast=None):
        return default
    class Csv:  # minimal stub
        def __init__(self, *args, **kwargs):
            pass

SECRET_KEY = config('DJANGO_SECRET_KEY', default='dev-insecure-change-me')
DEBUG = config('DJANGO_DEBUG', default=False, cast=lambda v: str(v).lower() in ('1','true','yes','on'))
_allowed = config('DJANGO_ALLOWED_HOSTS', default='*', cast=Csv())
if isinstance(_allowed, str):
    ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = list(_allowed) or ['*']
CSRF_TRUSTED_ORIGINS = [o for o in config('DJANGO_CSRF_TRUSTED_ORIGINS', default='', cast=str).split(',') if o]

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
    # 'rosetta',  # disabled (module not installed)

]

AUTH_USER_MODEL = "users.CustomUser"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
if DB_ENGINE.endswith('sqlite3'):
    DB_NAME = config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3'))
else:
    DB_NAME = config('DB_NAME', default='techstore')

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

# Ensure correct language persistence
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days

TIME_ZONE = config('TIME_ZONE', default='UTC')

USE_I18N = True

USE_TZ = True


STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'assets']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Email configuration (adjust credentials as needed)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER or 'webmaster@localhost')

# django-parler configuration
PARLER_LANGUAGES = {
    None: (
        {'code': 'ru'},
        {'code': 'en'},
        {'code': 'uz'},
    ),
    'default': {
        'fallbacks': ['ru'],  # default language
        'hide_untranslated': False,
    }
}

# ------------------------------------------------------------------
# Security hardening (only effective when DEBUG=False)
# ------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = config('DJANGO_SECURE_SSL_REDIRECT', default=True, cast=lambda v: str(v).lower() in ('1','true','yes','on'))
    SESSION_COOKIE_SECURE = config('DJANGO_SESSION_COOKIE_SECURE', default=True, cast=lambda v: str(v).lower() in ('1','true','yes','on'))
    CSRF_COOKIE_SECURE = config('DJANGO_CSRF_COOKIE_SECURE', default=True, cast=lambda v: str(v).lower() in ('1','true','yes','on'))
    SECURE_HSTS_SECONDS = config('DJANGO_SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = config('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=lambda v: str(v).lower() in ('1','true','yes','on'))
    SECURE_HSTS_PRELOAD = config('DJANGO_SECURE_HSTS_PRELOAD', default=True, cast=lambda v: str(v).lower() in ('1','true','yes','on'))
    SECURE_REFERRER_POLICY = config('DJANGO_SECURE_REFERRER_POLICY', default='strict-origin-when-cross-origin')
    SECURE_BROWSER_XSS_FILTER = config('DJANGO_SECURE_BROWSER_XSS_FILTER', default=True, cast=lambda v: str(v).lower() in ('1','true','yes','on'))
    SECURE_CONTENT_TYPE_NOSNIFF = config('DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True, cast=lambda v: str(v).lower() in ('1','true','yes','on'))
    X_FRAME_OPTIONS = config('DJANGO_X_FRAME_OPTIONS', default='DENY')

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
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

# ------------------------------------------------------------------
# Local developer overrides
# ------------------------------------------------------------------
try:  # noqa
    from .local_settings import *  # type: ignore
except ImportError:
    pass
