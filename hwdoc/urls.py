# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab
'''
Module containing hwdoc URLconf
'''

from django.conf.urls.defaults import *

urlpatterns = patterns('servermon.hwdoc.views',
            (r'^$', 'index'),
            (r'^project/(?P<project_id>[\d]+)/$', 'project'),
            (r'^equipment/(?P<equipment_id>[\d]+)/$', 'equipment'),
            (r'^search/$', 'search'),
            (r'^advancedsearch/$', 'advancedsearch'),
            # Opensearch
            url(r'^opensearch.xml$', 'opensearch', name="opensearch"),
            url(r'^suggest$', 'suggest', name="opensearchsuggestions"),
            )

