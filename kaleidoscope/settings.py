from os import getenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = getenv(
    'SECRET_KEY',
    'django-insecure-^l1fx@puo!r-ip2+dct1m1!2dt51f&v^d+_t^+s7+-x&f(4wdm'
)

DEBUG = getenv("DEBUG", "false").strip().lower() in ("1", "true", "yes")

DEFAULT_DOMAIN = getenv('DEFAULT_DOMAIN', 'localhost')
EXTRA_DOMAIN = getenv('EXTRA_DOMAIN', '')

ALLOWED_HOSTS = [
    DEFAULT_DOMAIN
]

CSRF_TRUSTED_ORIGINS = [
    f"https://{DEFAULT_DOMAIN}",
]

if EXTRA_DOMAIN != '':
    ALLOWED_HOSTS += [EXTRA_DOMAIN]
    CSRF_TRUSTED_ORIGINS += [f"https://{EXTRA_DOMAIN}"]
    X_FRAME_OPTIONS = f"ALLOW-FROM https://{EXTRA_DOMAIN}/"

EMBED_PARENT_ORIGIN = getenv('EMBED_PARENT_ORIGIN', '').strip()

INTERNAL_HOSTS = getenv('INTERNAL_HOSTS', '')
if INTERNAL_HOSTS:
    ALLOWED_HOSTS += [host.strip() for host in INTERNAL_HOSTS.split(',') if host.strip()]

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/images/'
LOGOUT_REDIRECT_URL = '/images/'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'imagekit',
    'django_bootstrap5',
    'dal_select2',
    'tables',
    'core',
    'dal'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kaleidoscope.urls'

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
                'core.context_processors.embed',
            ],
        },
    },
]

WSGI_APPLICATION = 'kaleidoscope.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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


LANGUAGE_CODE = 'sr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
LANGUAGES = [
    ('sr', 'Српски (Ћирилица)'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = 'static/'
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "kaleidoscope.storage.JsModuleManifestStaticFilesStorage",
    },
}

IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = 'tables.imagekit_strategies.GenerateOnSaveAndDemand'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': MEDIA_ROOT / '.imagekit-cache',
    }
}

WATERMARK_FONT_PATH = getenv(
    "WATERMARK_FONT_PATH",
    str(BASE_DIR / 'assets' / 'fonts' / 'DejaVuSans-Bold.ttf'),
)

IMAGE_WATERMARK_TEXT = getenv("IMAGE_WATERMARK_TEXT", "Klub Gacana")
IMAGE_WATERMARK_OPACITY = int(getenv("IMAGE_WATERMARK_OPACITY", "50"))
IMAGE_WATERMARK_SCALE = float(getenv("IMAGE_WATERMARK_SCALE", "0.50"))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if DEBUG:
    ALLOWED_HOSTS += [
        "127.0.0.1"
    ]
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
    INSTALLED_APPS += [
        'debug_toolbar',
    ]
    INTERNAL_IPS = ['127.0.0.1', ]

    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }
