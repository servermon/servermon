from settings_test import *  # noqa

DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'  # noqa
DATABASES['default']['NAME'] = 'servermon-test.db'  # noqa
