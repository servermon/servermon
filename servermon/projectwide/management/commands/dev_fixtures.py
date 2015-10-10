# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2015 Alexandros Kosiaris
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHORS DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
'''
Django management command to create development fixtures
'''

import string
import random
import sys
import os
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _l

from optparse import make_option
from django.db import transaction

from puppet.models import Fact, Host, FactValue
from updates.models import Package, Update
from hwdoc.models import Email, Phone, Person, Project, Role, \
    Vendor, RackModel, Datacenter, RackRow, Rack, RackPosition, \
    EquipmentModel, Equipment, ServerManagement, Storage
from django.core.management import call_command

PRODUCT_NAMES = {
    'Dell': [
        'PowerEdge 1950',
        'PowerEdge 2950',
        'Poweredge R610',
        'Poweredge R820',
    ],
    'HP': [
        'Proliant DL380 G1',
        'Proliant DL380 G2',
        'Proliant DL380 G3',
        'Proliant DL380 G4',
        'Proliant DL380 G5',
        'Proliant DL385 G3',
        'Proliant DL385 G4',
        'Proliant DL385 G5',
    ],
    'Fujitsu': [
        'PRIMERGY RX200 S5',
        'PRIMERGY RX200 S6',
        'PRIMERGY RX200 S7',
    ],
    'IBM': [
        'System x3550',
    ],
    'Someother': [
        'Random model 1',
        'Random model 2',
        'Random model 3',
        'Random model 4',
    ],
}


class Command(BaseCommand):
    '''
    Django management command to create development fixtures
    '''
    help = _l('''Create development fixtures. WARNING: This function is for
    development purposes only. It will abuse transcation and the database in
    awful ways. DO NOT RUN IT in production. You need --yes_force_run''')

    option_list = BaseCommand.option_list + (
        make_option('-y', '--yes_force_run',
                    action='store_true',
                    dest='yes_force_run',
                    default=False,
                    help=_l('Required. Force the run to happen')),
        make_option('-n', '--dry_run',
                    action='store_true',
                    dest='dry_run',
                    default=False,
                    help=_l('Dry run, mostly for testing the generation itself')),
        make_option('--fact_number',
                    action='store',
                    type='int',
                    dest='fact_number',
                    default=20,
                    help=_l('Number of facts to autocreate')),
        make_option('--host_number',
                    action='store',
                    type='int',
                    dest='host_number',
                    default=200,
                    help=_l('Number of hosts to autocreate')),
        make_option('--package_number',
                    action='store',
                    type='int',
                    dest='package_number',
                    default=200,
                    help=_l('Number of packages to autocreate')),
        make_option('--email_number',
                    action='store',
                    type='int',
                    dest='email_number',
                    default=20,
                    help=_l('Number of emails to autocreate')),
        make_option('--phone_number',
                    action='store',
                    type='int',
                    dest='phone_number',
                    default=20,
                    help=_l('Number of phones to autocreate')),
        make_option('--person_number',
                    action='store',
                    type='int',
                    dest='person_number',
                    default=20,
                    help=_l('Number of persons to autocreate')),
        make_option('--project_number',
                    action='store',
                    type='int',
                    dest='project_number',
                    default=20,
                    help=_l('Number of projects to autocreate')),
        make_option('--rackmodel_number',
                    action='store',
                    type='int',
                    dest='rackmodel_number',
                    default=20,
                    help=_l('Number of rackmodels to autocreate')),
        make_option('--datacenter_number',
                    action='store',
                    type='int',
                    dest='datacenter_number',
                    default=5,
                    help=_l('Number of datacenter to autocreate')),
        make_option('--rackrow_number',
                    action='store',
                    type='int',
                    dest='rackrow_number',
                    default=20,
                    help=_l('Number of rack_rows to autocreate')),
        make_option('--rack_number',
                    action='store',
                    type='int',
                    dest='rack_number',
                    default=80,
                    help=_l('Number of rack to autocreate')),
        make_option('--storage_number',
                    action='store',
                    type='int',
                    dest='storage_number',
                    default=7,
                    help=_l('Number of storages to autocreate')),
        make_option('--equipment_number',
                    action='store',
                    type='int',
                    dest='equipment_number',
                    default=1000,
                    help=_l('Number of equipment to autocreate')),
    )

    well_known_facts = {
        'interfaces': lambda x: random.choice(['eth0', 'eth0,eth1', 'eth0,eth1,eth2', 'eth0,eth1,eth2,eth3', ]),
        'macaddress_eth0': lambda x: '%s:%s:%s:%s:%s:%s' % (
            Command.id_generator(2), Command.id_generator(2),
            Command.id_generator(2), Command.id_generator(2),
            Command.id_generator(2), Command.id_generator(2)),
        'ipaddress_eth0': lambda x: x.ip,
        'netmask_eth0': lambda x: random.choice(['21', '23', '24', '25', '26', '27', ]),
        'ip6address_eth0': lambda x: '2a02:100:200:300:400:500:600:700',
        'operatingsystem': lambda x: random.choice(['Ubuntu', 'Debian', 'CentOS', ]),
        'operatingsystemrelease': lambda x: random.choice(['10.04', '8.0', '12.04', '6.0']),
        'memorytotal': lambda x: random.choice(['16GB', '24GB', '48GB', ]),
        'memoryfree': lambda x: random.choice(['2GB', '4GB', '6GB', ]),
        'serialnumber': lambda x: Command.id_generator(random.randint(6, 15)).upper(),
        'bios_date': lambda x: random.choice(['10/01/2015', '20/05/2013', '10/03/2010']),
        'bios_version': lambda x: random.choice(['1.2', '1.3', '3.5']),
        'manufacturer': lambda x: random.choice(['Dell', 'HP', 'IBM', 'Fujitsu', 'Someother']),
        'productname': lambda x: random.choice(PRODUCT_NAMES[x.manufacturer]),
        'processorcount': lambda x: random.choice(['2', '4', '6', '8', '16', '24', '48']),
        'architecture': lambda x: random.choice(['amd64', 'i386']),
        'virtual': lambda x: random.choice(['True', 'False']),
        'uptime': lambda x: Command.id_generator(20),
    }

    @transaction.commit_manually
    def handle(self, *args, **options):
        '''
        Handle command
        '''
        if not options['yes_force_run']:
            print '--yes_force_run not specified. Read help before continuing'
            return

        # Those will be rolledback, so no worries
        try:
            Fact.objects.all().delete()
            Host.objects.all().delete()
            Package.objects.all().delete()
            Update.objects.all().delete()
            Package.objects.all().delete()
            Email.objects.all().delete()
            Phone.objects.all().delete()
            Person.objects.all().delete()
            Project.objects.all().delete()
            Role.objects.all().delete()
            Vendor.objects.all().delete()
            RackModel.objects.all().delete()
            Datacenter.objects.all().delete()
            RackRow.objects.all().delete()
            Rack.objects.all().delete()
            RackPosition.objects.all().delete()
            EquipmentModel.objects.all().delete()
            Equipment.objects.all().delete()
            ServerManagement.objects.all().delete()

            # Puppet
            self.create_puppet_facts(options['fact_number'])
            self.create_puppet_hosts(options['host_number'])
            self.create_puppet_fact_values()

            # Updates
            self.create_updates_packages(options['package_number'])
            self.create_updates_updates()

            # Allocations
            self.create_hwdoc_emails(options['email_number'])
            self.create_hwdoc_phones(options['phone_number'])
            self.create_hwdoc_persons(options['person_number'])
            self.create_hwdoc_projects(options['project_number'])
            self.create_hwdoc_roles()

            # Equipment
            self.create_hwdoc_vendors()
            self.create_hwdoc_equipmentModels()
            self.create_hwdoc_rackmodels(options['rackmodel_number'])
            self.create_hwdoc_datacenters(options['datacenter_number'])
            self.create_hwdoc_rackrows(options['rackrow_number'])
            self.create_hwdoc_racks(options['rack_number'])
            self.create_hwdoc_storages(options['storage_number'])
            self.create_hwdoc_equipments(options['equipment_number'])
            # Keep stdout
            stdout = sys.stdout
            if options['dry_run']:
                transaction.rollback()
                return

            for i in ['puppet', 'updates', 'hwdoc']:
                # Note: The with construct does not play well with this as the
                # resource will be closed when calling the function
                try:
                    os.mkdir('servermon/%s/fixtures/' % i)
                except OSError:
                    pass
                f = open('servermon/%s/fixtures/sampledata.json' % i, 'w')
                # Redirect so we get data
                sys.stdout = f
                call_command('dumpdata', i, format='json', indent=2)
                # Restore stdout
                sys.stdout = stdout
                f.close()
        except Exception as e:
            print 'Error: %s, %s' % (e.__class__, e.message)
        # Unconditionally rollback always. We just pummeled the database for
        # nothing
        transaction.rollback()

    @classmethod
    def id_generator(cls, size=6, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for i in range(size))

    def create_puppet_facts(self, fact_number):
        facts = []
        print 'Creating %s puppet facts' % fact_number
        for i in range(fact_number):
            fact_name = Command.id_generator(random.randint(6, 30))
            facts.append(Fact(name=fact_name))
        # And some well known facts
        facts.extend(map(lambda x: Fact(name=x), self.well_known_facts.keys()))
        Fact.objects.bulk_create(facts)

    def create_puppet_hosts(self, host_number, domain_name='example.com'):
        hosts = []
        print 'Creating %s puppet hosts' % host_number
        for i in range(host_number):
            hostname = '%s.%s' % (Command.id_generator(random.randint(6, 20)), domain_name)
            print 'Created host: %s' % hostname
            ip = '%s.%s.%s.%s' % (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255), random.randint(1, 255))
            hosts.append(Host(
                name=hostname,
                ip=ip,
                environment=''))
        Host.objects.bulk_create(hosts)

    def create_puppet_fact_values(self):
        fact_values = []
        facts = list(Fact.objects.exclude(name__in=self.well_known_facts.keys()))  # Fetch them all as an optimization
        hosts = list(Host.objects.all())  # Fetch them all
        for host in hosts:
            host_facts = [random.choice(facts) for i in range(random.randint(0, len(facts)))]
            print 'Creating %s fact values for host %s' % (
                len(host_facts), host)
            for fact in host_facts:
                fact_values.append(FactValue(
                    fact_name=fact,
                    host=host,
                    value=Command.id_generator(random.randint(4, 5000))
                ))
            wk_facts = Fact.objects.filter(name__in=self.well_known_facts.keys())
            for wk_fact in wk_facts:
                value = self.well_known_facts[wk_fact.name](host)
                fact_values.append(FactValue(
                    fact_name=wk_fact,
                    host=host,
                    value=value)
                )
                # This is a hack to get fact value lookups before saving
                setattr(host, wk_fact.name, value)
        FactValue.objects.bulk_create(fact_values)

    def create_updates_packages(self, package_number):
        packages = []
        print 'Creating %s packages' % package_number
        for i in range(package_number):
            package_name = Command.id_generator(random.randint(6, 30))
            packages.append(Package(name=package_name, sourcename=package_name))
        Package.objects.bulk_create(packages)

    def create_updates_updates(self):
        updates = []
        packages = list(Package.objects.all())  # Fetch them all as an optimization
        hosts = list(Host.objects.all())  # Fetch them all
        for host in hosts:
            host_packages = list(set(
                [random.choice(packages) for x in range(random.randint(0, len(packages)))]))
            print 'Creating %s package updates for host %s' % (
                len(host_packages), host)
            for package in host_packages:
                updates.append(Update(
                    package=package,
                    host=host,
                    installedVersion=random.choice(['1.0-1', '1.5-2', '1.0-2', '4.2-1', '5.6']),
                    candidateVersion=random.choice(['1.0-2', '1.5-3', '1.0-6', '4.3-1', '5.7']),
                    source=Command.id_generator(5),
                    origin=random.choice(['Debian', 'Ubuntu']),
                    is_security=random.choice([True, False]),
                ))
        Update.objects.bulk_create(updates)

    # Allocations
    def create_hwdoc_emails(self, email_number, domain_name='example.com'):
        emails = []
        print 'Creating %s emails' % email_number
        for i in range(email_number):
            email = Command.id_generator(random.randint(6, 10)) + '@%s' % domain_name
            emails.append(Email(email=email))
        Email.objects.bulk_create(emails)

    def create_hwdoc_phones(self, phone_number):
        phones = []
        print 'Creating %s phones' % phone_number
        for i in range(phone_number):
            phone = Command.id_generator(10, chars='0123456789')
            phones.append(Phone(number=phone))
        Phone.objects.bulk_create(phones)

    # Yes I know the plural is people, this is on purpose
    def create_hwdoc_persons(self, person_number):
        emails = list(Email.objects.all())  # Fetch them all as an optimization
        phones = list(Phone.objects.all())  # Fetch them all
        print 'Creating %s persons' % person_number
        for i in range(person_number):
            person_emails = list(set(
                [random.choice(emails) for i in range(random.randint(1, 2))]))
            person_phones = list(set(
                [random.choice(phones) for i in range(random.randint(1, 3))]))
            person_name = Command.id_generator(random.randint(3, 10)).capitalize()
            person_surname = Command.id_generator(random.randint(3, 10)).capitalize()
            p = Person(name=person_name, surname=person_surname)
            p.save()
            p.emails.add(*person_emails)
            p.phones.add(*person_phones)

    def create_hwdoc_projects(self, project_number):
        projects = []
        print 'Creating %s projects' % project_number
        for i in range(project_number):
            project = Command.id_generator(random.randint(6, 10)).capitalize()
            projects.append(Project(name=project))
        Project.objects.bulk_create(projects)

    def create_hwdoc_roles(self):
        roles = []
        projects = list(Project.objects.all())  # Fetch them all as an optimization
        people = list(Person.objects.all())
        for project in set([random.choice(projects) for x in range(1, len(projects))]):
            project_person = random.choice(people)
            print 'Creating 1 role for project %s' % project
            roles.append(Role(
                person=project_person,
                project=project,
                role='manager'))  # Let's hardcode it for now. It's unimporant anyway
        Role.objects.bulk_create(roles)

    # Equipment
    def create_hwdoc_vendors(self):
        vendor_names = FactValue.objects.filter(
            fact_name__name='manufacturer'
        ).distinct().values_list('value', flat=True)
        vendors = []
        print 'Creating %s vendors' % len(vendor_names)
        for v in vendor_names:
            vendors.append(Vendor(name=v))
        Vendor.objects.bulk_create(vendors)

    def create_hwdoc_rackmodels(self, rackmodel_number):
        rackmodels = []
        vendors = list(Vendor.objects.all())  # Fetch them all as an optimization
        print 'Creating %s rackmodels' % rackmodel_number
        for i in range(rackmodel_number):
            rackmodel = Command.id_generator(random.randint(6, 10))
            rackmodels.append(RackModel(
                name=rackmodel,
                min_mounting_depth=random.choice([20, 25, 35, 40]),
                max_mounting_depth=random.choice([40, 50, 60]),
                height=random.choice([30, 40, 42, 50, 52]),
                width=random.choice([40, 50, 60]),
                inrow_ac=random.choice([False, False, False, True]),  # 1/4 is AC
                vendor=random.choice(vendors),
            ))
        RackModel.objects.bulk_create(rackmodels)

    def create_hwdoc_equipmentModels(self):
        hosts = list(Host.objects.all())
        tmp = set()
        for host in hosts:
            tmp.add((
                host.get_fact_value('manufacturer'),
                host.get_fact_value('productname'),
            ))

        equipmentmodels = list()
        print 'Creating %s equipmentmodels' % len(tmp)
        for t in tmp:
            equipmentmodels.append(EquipmentModel(
                name=t[1],
                vendor=Vendor.objects.get(name=t[0]),
                u=random.randint(1, 10),
            ))
        EquipmentModel.objects.bulk_create(equipmentmodels)

    def create_hwdoc_datacenters(self, datacenter_number):
        datacenters = []
        print 'Creating %s datacenters' % datacenter_number
        for i in range(datacenter_number):
            datacenter = Command.id_generator(random.randint(6, 10)).capitalize()
            datacenters.append(Datacenter(name=datacenter))
        Datacenter.objects.bulk_create(datacenters)

    def create_hwdoc_rackrows(self, rackrow_number):
        rackrows = []
        dcs = list(Datacenter.objects.all())  # Fetch them all as an optimization
        print 'Creating %s rackrows' % rackrow_number
        for i in range(rackrow_number):
            rackrow = Command.id_generator(random.randint(6, 10)).upper()
            rackrows.append(
                RackRow(name=rackrow, dc=random.choice(dcs))
            )
        RackRow.objects.bulk_create(rackrows)

    def create_hwdoc_racks(self, rack_number):
        rackmodels = list(RackModel.objects.all())  # Fetch them all as an optimization
        rackrows = list(RackRow.objects.all())
        print 'Creating %s racks' % rack_number
        for i in range(rack_number):
            rack = Command.id_generator(random.randint(4, 8)).upper()
            r = Rack(
                name=rack,
                model=random.choice(rackmodels))
            r.save()
            rp = RackPosition(
                rack=r,
                position=random.randint(0, 8),
                rr=random.choice(rackrows))
            rp.save()

    def create_hwdoc_storages(self, storage_number):
        datacenters = list(Datacenter.objects.all())
        storages = []
        print 'Creating %s datacenters' % storage_number
        for i in range(storage_number):
            storage = Command.id_generator(random.randint(6, 10)).capitalize()
            storages.append(Storage(name=storage,
                                    dc=random.choice(datacenters)))
        Storage.objects.bulk_create(storages)

    def create_hwdoc_equipments(self, equipment_number, domain_name='example.com'):
        equipments = []
        hosts = list(Host.objects.all())  # Fetch them all as an optimization
        racks = list(Rack.objects.all())  # Fetch them all as an optimization
        storages = list(Storage.objects.all())
        projects = list(Project.objects.all())  # Fetch them all as an optimization
        print 'Creating %s equipments' % len(hosts)

        # This is really the NP-hard problem, discrete knapsack. Well, a
        # variation but solving it well is out of the scope, so using a dumb
        # probabilistic algorith to assign a box a u
        def assign_u(e):
            rack = None
            units = None
            for i in range(len(racks)):
                tmp = random.choice(racks)
                if tmp.model.inrow_ac:
                    continue
                # See if a rack possibly fits us
                units = tmp.get_empty_units()
                if len(units) >= e.model.u:
                    rack = tmp
                    units = list(units)
                    break
            # No rack had even remotely space for us
            if not rack:
                return None, None
            # Pick a free u and check if the next u units are free
            # If not. just ignore the equipment
            start = random.choice(units)
            for i in range(e.model.u):
                if start + i not in units:
                    return None, None
            return rack, start

        for host in hosts:
            vendor = Vendor.objects.get(name=host.get_fact_value('manufacturer'))

            model = EquipmentModel.objects.get(vendor=vendor,
                                               name=host.get_fact_value('productname'))

            e = Equipment(
                model=model,
                serial=host.get_fact_value('serialnumber'))
            r, u = assign_u(e)
            if r:
                e.rack, e.unit = assign_u(e)
            elif random.randint(1, 10) >= 9:
                # 90% in some storage
                e.storage = random.choice(storages)
            # 50% allocated to a project
            if random.randint(1, 10) >= 5:
                e.allocation = random.choice(projects)
            # 10% having a test comment
            if random.randint(1, 10) == 10:
                e.comments = 'Test comment'
            equipments.append(e)
        Equipment.objects.bulk_create(equipments)
        # And now add ServerManagement to 70% of them
        eqs = list(Equipment.objects.all())
        servermanagements = []
        will_get_sm = random.sample(eqs, len(eqs) * 7 / 10)  # Too bored to do 0.7 and cast to int
        for i in will_get_sm:
            servermanagements.append(
                ServerManagement(
                    method='dummy',
                    hostname='%s.%s' % (Command.id_generator(random.randint(6, 20)), domain_name),
                    equipment=i,
                ))
        ServerManagement.objects.bulk_create(servermanagements)
