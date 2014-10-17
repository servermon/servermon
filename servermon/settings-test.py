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
    'south',
    'keyvalue',
)

AUTHENTICATION_BACKENDS = (
    'djangobackends.ldapBackend.ldapBackend',
    'django.contrib.auth.backends.ModelBackend',
    )

LDAP_AUTH_SETTINGS = (
    { 'url': 'ldap://localhost/', 'base': 'ou=People,dc=example,dc=org' },
)
