from settings import *

DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
DATABASES['default']['NAME'] = 'servermon-test.db'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'projectwide',
    'updates',
    'puppet',
    'hwdoc',
    'keyvalue',
)

if DJANGO_VERSION[:2] < (1, 7):
        INSTALLED_APPS = INSTALLED_APPS + ('south',)

AUTHENTICATION_BACKENDS = (
    'djangobackends.ldapBackend.ldapBackend',
    'django.contrib.auth.backends.ModelBackend',
    )

LDAP_AUTH_SETTINGS = (
    { 'url': 'ldap://localhost/', 'base': 'ou=People,dc=example,dc=org' },
)
