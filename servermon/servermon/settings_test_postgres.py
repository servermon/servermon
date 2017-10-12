from servermon.settings_test import *  # noqa

DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'  # noqa
DATABASES['default']['NAME'] = 'servermon'  # noqa
DATABASES['default']['USER'] = 'travis'  # noqa
