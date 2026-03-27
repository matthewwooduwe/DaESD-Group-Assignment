"""
Django settings for payment_gateway project.
"""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file(path):
    env_map = {}
    if not path.exists():
        return env_map
    for line in path.read_text(encoding='utf-8').splitlines():
        raw = line.strip()
        if not raw or raw.startswith('#') or '=' not in raw:
            continue
        key, value = raw.split('=', 1)
        env_map[key.strip()] = value.strip().strip('"').strip("'")
    return env_map


_secure_env_override = os.environ.get('PAYMENT_GATEWAY_SECURE_ENV_FILE')
if _secure_env_override:
    SECURE_ENV_FILES = [Path(_secure_env_override)]
else:
    # Support both legacy `env.secure` and preferred `.env.secure`.
    # If both exist, `.env.secure` takes precedence.
    SECURE_ENV_FILES = [BASE_DIR / 'env.secure', BASE_DIR / '.env.secure']

SECURE_ENV = {}
for _secure_path in SECURE_ENV_FILES:
    SECURE_ENV.update(_load_env_file(_secure_path))

# Backward-compatible debug/introspection variable.
SECURE_ENV_FILE = SECURE_ENV_FILES[-1]


def _secret(name, default=''):
    return os.environ.get(name) or SECURE_ENV.get(name) or default

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-change-me')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'payment_gateway.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'payment_gateway.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'brfn_db'),
        'USER': os.environ.get('DB_USER', 'brfn_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'brfn_password'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '3306'),
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


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CORS_ALLOW_ALL_ORIGINS = True

PLATFORM_API_URL = os.environ.get('PLATFORM_API_URL', 'http://platform-api:8002')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:8000')
PAYMENT_GATEWAY_URL = os.environ.get('PAYMENT_GATEWAY_URL', 'http://localhost:8003')

STRIPE_PUBLISHABLE_KEY = _secret(
    'STRIPE_PUBLISHABLE_KEY',
    _secret('PAYMENT_GATEWAY_PUBLISHABLE_KEY', ''),
)
STRIPE_SECRET_KEY = _secret(
    'STRIPE_SECRET_KEY',
    _secret('PAYMENT_GATEWAY_API_KEY', ''),
)
STRIPE_WEBHOOK_SECRET = _secret('STRIPE_WEBHOOK_SECRET', '')
STRIPE_CURRENCY = _secret('STRIPE_CURRENCY', 'gbp').lower()
