# SECURITY WARNING: don't run with debug turned on in production!
from .base import *

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



