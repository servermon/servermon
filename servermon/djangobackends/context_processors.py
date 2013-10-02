'''
Adds installed_apps related context variables to the context.
'''

from django.conf import settings

def installed_apps(request):
    '''
    Adds installed_apps related context variables to the context.
    '''

    return {'INSTALLED_APPS': settings.INSTALLED_APPS}
