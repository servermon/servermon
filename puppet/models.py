from django.db import models
from xml.dom.minidom import parseString

class Fact(models.Model):
    name = models.CharField(max_length=765)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'fact_names'
        ordering = [ 'name' ]

    def __unicode__(self):
        return self.name.replace('_',' ').rstrip()

class Host(models.Model):
    name = models.CharField(max_length=765)
    ip = models.CharField(max_length=765, blank=True)
    last_compile = models.DateTimeField(null=True, blank=True)
    last_freshcheck = models.DateTimeField(null=True, blank=True)
    last_report = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    source_file_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    facts = models.ManyToManyField(Fact, through='FactValue')

    class Meta:
        db_table = u'hosts'
        ordering = ['name',]

    def __unicode__(self):
        return self.name

    def get_fact_value(self, fact):
        try:
            return self.factvalue_set.get(fact_name__name=fact).value
        except:
            return None


class FactValue(models.Model):
    value = models.TextField()
    fact_name = models.ForeignKey(Fact)
    host = models.ForeignKey(Host)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'fact_values'

    def __unicode__(self):
        return "%s %s: %s" % (self.host.name, str(self.fact_name), self.value)

class ParamNames(models.Model):
    name = models.CharField(max_length=765)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'param_names'

class ParamValues(models.Model):
    value = models.TextField()
    param_name_id = models.IntegerField()
    line = models.IntegerField(null=True, blank=True)
    resource_id = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'param_values'

class PuppetTags(models.Model):
    name = models.CharField(max_length=765, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'puppet_tags'

class ResourceTags(models.Model):
    resource_id = models.IntegerField(null=True, blank=True)
    puppet_tag_id = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'resource_tags'

class Resources(models.Model):
    title = models.TextField()
    restype = models.CharField(max_length=765)
    host_id = models.IntegerField(null=True, blank=True)
    source_file_id = models.IntegerField(null=True, blank=True)
    exported = models.IntegerField(null=True, blank=True)
    line = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'resources'

class SourceFiles(models.Model):
    filename = models.CharField(max_length=765, blank=True)
    path = models.CharField(max_length=765, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'source_files'

