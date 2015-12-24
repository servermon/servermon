from settings_test import *  # noqa

DATABASES['default']['ENGINE'] = 'django.db.backends.mysql'
DATABASES['default']['NAME'] = 'servermon'
DATABASES['default']['USER'] = 'travis'
