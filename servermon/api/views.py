from rest_framework import viewsets
from serializers import (
    EquipmentSerializer, RackSerializer,
    ProjectSerializer, ServerManagementSerializer
)
from hwdoc.models import Equipment, Rack, Project, ServerManagement


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    filter_fields = ('serial',)


class RackViewSet(viewsets.ModelViewSet):
    queryset = Rack.objects.all()
    serializer_class = RackSerializer
    filter_fields = ('name',)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ServerManagementViewSet(viewsets.ModelViewSet):
    queryset = ServerManagement.objects.all()
    serializer_class = ServerManagementSerializer
    filter_fields = ('hostname', )
