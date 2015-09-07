# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('puppet', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('sourcename', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Update',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('installedVersion', models.CharField(max_length=200)),
                ('candidateVersion', models.CharField(max_length=200)),
                ('source', models.CharField(max_length=200)),
                ('origin', models.CharField(max_length=200, null=True)),
                ('is_security', models.BooleanField(default=False)),
                ('host', models.ForeignKey(to='puppet.Host')),
                ('package', models.ForeignKey(to='updates.Package')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='package',
            name='hosts',
            field=models.ManyToManyField(to='puppet.Host', through='updates.Update'),
            preserve_default=True,
        ),
    ]
