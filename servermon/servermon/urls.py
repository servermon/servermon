from django.conf import settings
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    (r'^/?$', 'projectwide.views.index'),  # noqa
    (r'^hosts/$', 'updates.views.hostlist'),
    (r'^hosts/(.*)', 'updates.views.host'),
    (r'^packages/$', 'updates.views.packagelist'),
    (r'^packages/(.*)', 'updates.views.package'),
    (r'^inventory/?$', 'puppet.views.inventory'),
    (r'^search/?$', 'projectwide.views.search'),
    (r'^advancedsearch/$', 'projectwide.views.advancedsearch'),
    (r'^query/?$', 'puppet.views.query'),
    # Opensearch
    url(r'^opensearch.xml$', 'projectwide.views.opensearch', name="opensearch"),
    url(r'^suggest/$', 'projectwide.views.suggest', name="opensearchsuggestions"),
)
if 'hwdoc' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^hwdoc/', include('hwdoc.urls')),  # noqa
    )

if 'django.contrib.admin' in settings.INSTALLED_APPS:
    from django.contrib import admin
    admin.autodiscover()
    urlpatterns += patterns('',
        (r'^admin/', include(admin.site.urls)),  # noqa
        (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    )

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.contrib.staticfiles.views.serve') # noqa
    )
