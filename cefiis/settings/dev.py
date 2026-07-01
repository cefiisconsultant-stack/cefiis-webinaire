from .base import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4ra#!+0@c-6gn^mg_szh3-y%fa^1r43qq67ww2ib@(imkowjp='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["021dc622d5e9.ngrok-free.app", "127.0.0.1", ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

MEDIA_URL = '/media/'
STATIC_URL = '/static/'

print(">> Chargement du fichier de configuration : DEV")