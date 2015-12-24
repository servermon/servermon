from settings_test import *  # noqa

DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
DATABASES['default']['NAME'] = 'servermon'
DATABASES['default']['USER'] = 'travis'
