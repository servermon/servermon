from rest_framework import routers
from api.views import (
    EquipmentViewSet, RackViewSet, ProjectViewSet, ServerManagementViewSet
)
from django import VERSION as DJANGO_VERSION
if DJANGO_VERSION[:2] >= (1, 4):
    from django.conf.urls import patterns, url, include
else:
    from django.conf.urls.defaults import patterns, url, include

router = routers.DefaultRouter()
router.register(r'equipment', EquipmentViewSet, 'equipment')
router.register(r'rack', RackViewSet, 'rack')
router.register(r'project', ProjectViewSet, 'project')
router.register(
    r'servermanagement', ServerManagementViewSet, 'servermanagement')

urlpatterns = patterns(
    '',
    url(r'^', include(router.urls), name='routed-urls'),
    # API auth is disabled as permissions have been set to block all users,
    # authenticated or not, from editing content
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
