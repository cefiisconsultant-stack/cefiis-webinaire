# SECURITY WARNING: don't run with debug turned on in production!
from .base import *
ALLOWED_HOSTS = ['webinaire.cefiis.com', 'cefiis.com', 'www.cefiis.com', '187.124.222.239', 'ebook.cefiis.com']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# remonter d’un dossier en plus pour avoir la racine souhaitée
ROOT_DIR = os.path.dirname(BASE_DIR)

DEBUG = False

MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_ROOT = os.path.join(ROOT_DIR, 'static')
MEDIA_ROOT = os.path.join(ROOT_DIR, 'media')

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

from decouple import config

EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
SERVER_EMAIL = config('DEFAULT_FROM_EMAIL')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

print(">> Chargement du fichier de configuration : PROD")



