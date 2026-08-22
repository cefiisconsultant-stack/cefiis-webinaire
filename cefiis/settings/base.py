from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-local-development-only-change-me",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'webinaire',
    'ebook',
    'vitrine',
    'diagnostic',
    'formations',
    'blog',
    
]
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

KKIAPAY_PUBLIC_KEY = config('KKIAPAY_PUBLIC_KEY')
INSCRIPTIONS_WEBINAIRE_OUVERTES = config('INSCRIPTIONS_WEBINAIRE_OUVERTES', default=True, cast=bool)
WEBINAIRE_DATE_ISO = config('WEBINAIRE_DATE_ISO', default='2026-08-01T16:00:00')
WEBINAIRE_DATE_AFFICHAGE = config('WEBINAIRE_DATE_AFFICHAGE', default='Samedi 1er août')
KKIAPAY_PRIVATE_KEY = config('KKIAPAY_PRIVATE_KEY')
KKIAPAY_SECRET_KEY = config('KKIAPAY_SECRET_KEY')
KKIAPAY_SANDBOX = config('KKIAPAY_SANDBOX', default=True, cast=bool)

# Réglages ebook
SITE_URL = config("SITE_URL", default="http://127.0.0.1:8000").rstrip("/")
EBOOK_PRICE = config("EBOOK_PRICE", default=2000, cast=int)
EBOOK_DOWNLOAD_MAX = config("EBOOK_DOWNLOAD_MAX", default=3, cast=int)
EBOOK_DOWNLOAD_EXPIRY_HOURS = config(
    "EBOOK_DOWNLOAD_EXPIRY_HOURS",
    default=72,
    cast=int,
)
EBOOK_FILE_PATH = Path(
    config(
        "EBOOK_FILE_PATH",
        default=str(
            BASE_DIR
            / "private"
            / "ebook"
            / "De_l_Expert_au_Consultant_Professionnel.pdf"
        ),
    )
)
EBOOK_SUPPORT_EMAIL = config(
    "EBOOK_SUPPORT_EMAIL",
    default="etiennegbedagbe@cefiis.com",
)
EBOOK_GUARANTEE_ENABLED = False
EBOOK_GUARANTEE_TEXT = (
    "Garantie satisfait ou remboursé pendant 7 jours. "
    "Si l'ebook ne vous apporte pas de valeur, écrivez-nous et nous vous remboursons intégralement."
)

# Liens WhatsApp pour le diagnostic / ebook
DIAGNOSTIC_WHATSAPP_GROUP_NAME = config(
    "DIAGNOSTIC_WHATSAPP_GROUP_NAME",
    default="De l'Expert au Consultant — Cefiis",
)
DIAGNOSTIC_WHATSAPP_GROUP_URL = config(
    "DIAGNOSTIC_WHATSAPP_GROUP_URL",
    default="",
)

# Google Tag Manager

GTM_ENABLED = config("GTM_ENABLED", default=False, cast=bool)

GTM_CONTAINER_ID = config(
    "GTM_CONTAINER_ID",
    default="",
).strip()

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'cefiis.middleware.GoogleTagManagerMiddleware',
]

ROOT_URLCONF = 'cefiis.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'cefiis.wsgi.application'

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.hostinger.com")
EMAIL_PORT = config("EMAIL_PORT", default=465, cast=int)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=True, cast=bool)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=EMAIL_HOST_USER or "etiennegbedagbe@cefiis.com",
)
SERVER_EMAIL = config("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)

 
