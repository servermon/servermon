# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Datacenter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Datacenter',
                'verbose_name_plural': 'Datacenters',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.CharField(max_length=80)),
            ],
            options={
                'verbose_name': 'Email',
                'verbose_name_plural': 'Emails',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serial', models.CharField(max_length=80)),
                ('unit', models.PositiveIntegerField(null=True, blank=True)),
                ('purpose', models.CharField(max_length=80, blank=True)),
                ('rack_front', models.BooleanField(default=True)),
                ('rack_interior', models.BooleanField(default=True)),
                ('rack_back', models.BooleanField(default=True)),
                ('orientation', models.CharField(default=b'Front', max_length=10, choices=[(b'Front', b'Front'), (b'Back', b'Back'), (b'NA', b'Not Applicable')])),
                ('comments', models.TextField(blank=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['rack', '-unit'],
                'verbose_name': 'Equipment',
                'verbose_name_plural': 'Equipments',
                'permissions': (('can_change_comment', 'Can change comments'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EquipmentModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80)),
                ('u', models.PositiveIntegerField(verbose_name=b'Us')),
            ],
            options={
                'ordering': ['vendor', 'name'],
                'verbose_name': 'Equipment Model',
                'verbose_name_plural': 'Equipment Models',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80)),
                ('surname', models.CharField(max_length=80)),
                ('emails', models.ManyToManyField(to='hwdoc.Email')),
            ],
            options={
                'verbose_name': 'Person',
                'verbose_name_plural': 'People',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(max_length=80)),
            ],
            options={
                'verbose_name': 'Phone',
                'verbose_name_plural': 'Phones',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mounted_depth', models.PositiveIntegerField(default=60, max_length=10)),
                ('name', models.CharField(max_length=80)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Rack',
                'verbose_name_plural': 'Racks',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RackModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80)),
                ('max_mounting_depth', models.PositiveIntegerField(max_length=10)),
                ('min_mounting_depth', models.PositiveIntegerField(max_length=10)),
                ('height', models.PositiveIntegerField(max_length=10)),
                ('width', models.PositiveIntegerField(max_length=10)),
                ('inrow_ac', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Rack Model',
                'verbose_name_plural': 'Rack Models',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RackPosition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveIntegerField(max_length=20)),
                ('rack', models.OneToOneField(to='hwdoc.Rack')),
            ],
            options={
                'ordering': ['position'],
                'verbose_name': 'Rack Position in Rack Row',
                'verbose_name_plural': 'Rack Positions in Rack Rows',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RackRow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80)),
                ('dc', models.ForeignKey(blank=True, to='hwdoc.Datacenter', null=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Rack Row',
                'verbose_name_plural': 'Rack Rows',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=80, choices=[(b'manager', b'Manager'), (b'technical', b'Techinal Person')])),
                ('person', models.ForeignKey(to='hwdoc.Person')),
                ('project', models.ForeignKey(to='hwdoc.Project')),
            ],
            options={
                'verbose_name': 'Role',
                'verbose_name_plural': 'Roles',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServerManagement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('method', models.CharField(max_length=10, choices=[(b'ilo2', b'HP iLO 2'), (b'ilo3', b'HP iLO 3'), (b'irmc', b'Fujitsu iRMC'), (b'ipmi', b'Generic IPMI'), (b'dummy', b'Dummy Method Backend')])),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('hostname', models.CharField(max_length=80)),
                ('username', models.CharField(max_length=80, blank=True)),
                ('password', models.CharField(max_length=80, blank=True)),
                ('license', models.CharField(max_length=80, blank=True)),
                ('raid_license', models.CharField(max_length=80, blank=True)),
                ('mac', models.CharField(max_length=17, blank=True)),
                ('equipment', models.OneToOneField(to='hwdoc.Equipment')),
            ],
            options={
                'verbose_name': 'Server Management',
                'verbose_name_plural': 'Servers Management',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=80)),
                ('dc', models.ForeignKey(to='hwdoc.Datacenter')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Storage',
                'verbose_name_plural': 'Storages',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=20)),
                ('state', models.CharField(max_length=10, choices=[(b'open', b'Open'), (b'closed', b'Closed')])),
                ('url', models.CharField(max_length=250, blank=True)),
                ('equipment', models.ManyToManyField(to='hwdoc.Equipment')),
            ],
            options={
                'verbose_name': 'Ticket',
                'verbose_name_plural': 'Tickets',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Vendor',
                'verbose_name_plural': 'Vendors',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='rackposition',
            name='rr',
            field=models.ForeignKey(to='hwdoc.RackRow'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rackmodel',
            name='vendor',
            field=models.ForeignKey(to='hwdoc.Vendor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rack',
            name='model',
            field=models.ForeignKey(to='hwdoc.RackModel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='contacts',
            field=models.ManyToManyField(to='hwdoc.Person', through='hwdoc.Role'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='phones',
            field=models.ManyToManyField(to='hwdoc.Phone'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='equipmentmodel',
            name='vendor',
            field=models.ForeignKey(to='hwdoc.Vendor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='equipment',
            name='allocation',
            field=models.ForeignKey(blank=True, to='hwdoc.Project', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='equipment',
            name='model',
            field=models.ForeignKey(to='hwdoc.EquipmentModel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='equipment',
            name='rack',
            field=models.ForeignKey(blank=True, to='hwdoc.Rack', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='equipment',
            name='storage',
            field=models.ForeignKey(blank=True, to='hwdoc.Storage', null=True),
            preserve_default=True,
        ),
    ]
