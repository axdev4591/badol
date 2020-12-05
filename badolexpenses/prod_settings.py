import dj_database_url
from .settings import *

from decouple import config, Csv


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='s3cr3t_k3y')


ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='127.0.0.1,localhost')

DEBUG = False
TEMPLATE_DEBUG = False

DATABASES['default'] = dj_database_url.config()

MIDDLEWARE += ['whitenoise.middleware.WhiteNoiseMiddleware']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' 
