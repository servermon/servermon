# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab
'''
Module containing hwdoc URLconf
'''

from django.conf.urls.defaults import *

urlpatterns = patterns('servermon.hwdoc.views',
            (r'^$', 'index'),
            (r'^subnav/(?P<subnav>[\w]+)/$', 'subnav'),
            (r'^flotdata/(?P<datatype>[\w]+)/$', 'flotdata'),
            (r'^project/(?P<project_id>[\d]+)/$', 'project'),
            (r'^equipment/(?P<equipment_id>[\d]+)/$', 'equipment'),
            (r'^equipment/unallocated$', 'unallocated_equipment'),
            (r'^equipment/commented$', 'commented_equipment'),
            (r'^equipment/ticketed$', 'ticketed_equipment'),
            (r'^rack/(?P<rack_id>[\d]+)/$', 'rack'),
            (r'^rackrow/(?P<rackrow_id>[\d]+)/$', 'rackrow'),
            (r'^datacenter/(?P<datacenter_id>[\d]+)/$', 'datacenter'),
            )

