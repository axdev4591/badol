from badolexpenses.settings import *
import dj_database_url


DEBUG = False
TEMPLATE_DEBUG = False

DATABASE['default'] = dj_database_url.config()

SECRET_KEY = 'kr8u^6y3vf$(v#$cb7cb=duto*c-+e41&3*4&d*pm_43m@!%x^'

ALLOWED_HOSTS = ['badol.herokuapp.com'] 