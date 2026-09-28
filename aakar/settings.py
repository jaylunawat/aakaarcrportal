# In aakar/settings.py

import os
from importlib.util import find_spec
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    return [item.strip() for item in os.getenv(name, default).split(',') if item.strip()]


DEBUG = env_bool('DJANGO_DEBUG', True)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = get_random_secret_key()
    else:
        raise ImproperlyConfigured('DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is false.')

ALLOWED_HOSTS = env_list(
    'DJANGO_ALLOWED_HOSTS',
    '127.0.0.1,localhost,crportal.aakaariitb.org.in,www.crportal.aakaariitb.org.in',
)


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "aakarapp",
    'import_export',

    # Allauth apps
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'allauth.account.middleware.AccountMiddleware',
]

if find_spec('whitenoise'):
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = "aakar.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = "aakar.wsgi.application"


# Database
database_url = os.getenv('DATABASE_URL')
if database_url:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(
            database_url,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=env_bool('DATABASE_SSL_REQUIRED', True),
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator", },
    { "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    { "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    { "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv('DJANGO_TIME_ZONE', 'Asia/Kolkata')
USE_I18N = True
USE_TZ = True


# Static and Media files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_ROOT = Path(os.getenv('DJANGO_MEDIA_ROOT', BASE_DIR / 'media'))
MEDIA_URL = '/media/'

if find_spec('whitenoise'):
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# HTTPS SETTINGS (For production)
CSRF_TRUSTED_ORIGINS = env_list(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    'https://crportal.aakaariitb.org.in,https://www.crportal.aakaariitb.org.in',
)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', False) and not DEBUG
SECURE_HSTS_SECONDS = int(os.getenv('DJANGO_SECURE_HSTS_SECONDS', '0' if DEBUG else '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'


# --- ALLAUTH SETTINGS (MERGED AND CORRECTED) ---

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

LOGIN_REDIRECT_URL = '/cr/dashboard'
LOGOUT_REDIRECT_URL = '/cr'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Skips the intermediate "Sign In" confirmation page
SOCIALACCOUNT_LOGIN_ON_GET = True

# --- SETTINGS FOR CUSTOM GOOGLE SIGN-IN FLOW ---
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_ADAPTER = 'aakarapp.adapter.MySocialAccountAdapter'


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [ 'profile', 'email', ],
        'AUTH_PARAMS': { 'access_type': 'online', }
    }
}


# --- EMAIL SETTINGS ---
# For local development, emails are printed to the console.
# For production, you must fill these with your details from Hostinger.
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend',
)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.hostinger.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'webmaster@localhost')
