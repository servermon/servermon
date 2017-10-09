from rest_framework import serializers
from hwdoc.models import (
    Equipment, Rack, EquipmentModel, Project, ServerManagement
)


class EquipmentModelSerializer(serializers.HyperlinkedModelSerializer):

    vendor = serializers.SerializerMethodField('get_vendor')

    def get_vendor(self, obj):
        return obj.vendor

    class Meta:
        model = EquipmentModel
        fields = (
            'name',
            'vendor'
        )


class EquipmentSerializer(serializers.HyperlinkedModelSerializer):

    # the following fields derive from methods' output values
    project = serializers.SerializerMethodField('get_allocation')
    rack = serializers.SerializerMethodField('get_rack')
    keyvalue_attrs = serializers.SerializerMethodField('get_attrs')
    ipmi = serializers.SerializerMethodField('get_ipmi')
    model = EquipmentModelSerializer()
    datacenter = serializers.SerializerMethodField('get_dc_name')

    # used to get value from 'allocation' field.
    # We need this to be able to display 'allocation'
    # with a different name
    def get_allocation(self, obj):
        try:
            return obj.allocation
        except:
            return None

    def get_rack(self, obj):
        try:
            rack = obj.rack.name
            unit = obj.unit
        except Exception:
            rack = None
            unit = None
        return {
            'rack': rack,
            'rackunit': unit,
        }

    def get_ipmi(self, obj):
        try:
            host = obj.servermanagement.hostname
            mac = obj.servermanagement.mac
        except Exception:
            host = None
            mac = None
        return {
            'IPMI Hostname': host,
            'IPMI Mac': mac
        }

    def get_dc_name(self, obj):
        try:
            return obj.dc.name
        except:
            return None

    def get_attrs(self, obj):

        pairs = dict()
        try:
            attrs = obj.attrs.all()
        except:
            attrs = None
        if attrs:
            for attr in attrs:
                pairs.update({
                    attr.key.name: attr.value
                })
        return pairs

    class Meta:
        model = Equipment
        fields = (
            'serial', 'ipmi', 'model', 'datacenter', 'rack', 'unit',
            'orientation', 'project', 'purpose', 'comments', 'keyvalue_attrs',
        )


class RackSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Rack
        fields = (
            'mounted_depth', 'name'
        )


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Project
        fields = (
            'name',
        )


class ServerManagementSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ServerManagement
        fields = (
            'mac', 'hostname', 'method'
        )
