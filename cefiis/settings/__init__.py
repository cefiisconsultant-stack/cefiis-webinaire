import os
from pathlib import Path
from decouple import config

# Valeur par défaut : development
ENV = config('DJANGO_ENV')

if ENV == 'production':
    from .prod import *
elif ENV == 'development':
    from .dev import *
