from settings import *  # noqa

DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'  # noqa
DATABASES['default']['NAME'] = 'servermon-test.db'  # noqa

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'projectwide',
    'updates',
    'puppet',
    'hwdoc',
    'keyvalue',
)

if DJANGO_VERSION[:2] < (1, 7):  # noqa
        INSTALLED_APPS = INSTALLED_APPS + ('south',)

AUTHENTICATION_BACKENDS = (
    'djangobackends.ldapBackend.ldapBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LDAP_AUTH_SETTINGS = (
    {'url': 'ldap://localhost/', 'base': 'ou=People,dc=example,dc=org'},
)

# We want to manage puppet models while performing tests in order to create the
# database tables
MANAGED_PUPPET_MODELS = True
