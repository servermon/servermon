from servermon.settings_test import *  # noqa

DATABASES['default']['ENGINE'] = 'django.db.backends.mysql'  # noqa
DATABASES['default']['NAME'] = 'servermon'  # noqa
DATABASES['default']['USER'] = 'travis'  # noqa
