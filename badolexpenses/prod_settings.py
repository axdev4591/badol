import dj_database_url
from .settings import *
import os



DEBUG = True
TEMPLATE_DEBUG = False

#DATABASES['default'] = dj_database_url.config()

MIDDLEWARE += ['whitenoise.middleware.WhiteNoiseMiddleware']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' 


#SECRET_KET = os.environ['SECRET_KET']

ALLOWED_HOSTS = ['badol.herokuapp.com'] 
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True