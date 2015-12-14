Servermon installation tutorial
===============================

Documents Servermon version 0.7.0

.. contents::

Introduction
------------

Servermon is a server monitoring/reporting software based on Django and
Puppet. This document describes how to install and configure it

A basic Servermon terminology glossary is provided in the introductory
section of the :doc:`glossary`. Please refer to that document if you are
uncertain about the terms we are using.

Servermon has been developed for Linux and should be distribution-agnostic.
This documentation will use Debian Squeeze as an example system but the
examples can be translated to any other distribution. You are expected
to be familiar with your distribution and its package management system.

This document is divided into two main sections:

- Installation

- Configuration of the environment for Servermon

Each of these is divided into sub-sections. While a full Servermon
installation will need all of the steps specified, some are not strictly
required for every environment. Which ones they are, and why, is specified in
the corresponding sections.

Servermon at this point offers two applications

1) A Web frontend to the Puppet database.
2) hwdoc: A simple datacenter hardware documentation database

If you have no idea what Puppet is, it is possible that you don't need
this software. Do note however that hwdoc will still be usable even
without a Puppet infrastructure

Installation
------------

Hardware requirements
+++++++++++++++++++++

Any system supported by your Linux distribution is fine. 64-bit systems
are the ones tested better but there is no reason 32-bit systems should
not work. You dont even really need a Linux system! BSD's and Windows
should work fine too but you will find no documentation here on how to
install on them

Software requirements
+++++++++++++++++++++

Any Linux distribution should be fine. BSD's and Windows should be fine
too. That being said, the software is written and tested mostly on
Debian and Ubuntu and only occasionally on FreeBSD so your best bet is a
Debian or a Debian derivative system. The rest of the documentation
assumes a Debian system, please adjust accordingly

Installing the software
+++++++++++++++++++++++

**Mandatory**.

Python, Django, South is needed.

Use system provided packages::

  $ aptitude install python-django
  $ aptitude install python-django-south
  $ aptitude install python-whoosh
  $ aptitude install python-ipy
  $ aptitude install python-mysqldb (or sqlite or psycopg2)
  $ aptitude install python-ldap (for user authentication via LDAP)

Installation using pip::

  $ pip install -r requirements.txt

Deploy the software::

  $ mkdir /path/to/servermon
  $ tar xfvz servermon-X.Y.tar.gz -C /path/to/servermon

A Puppet infrastructure with an RDBMS (MySQL, PostgreSQL) is needed for
everything else apart from hwdoc

An application server. Gunicorn should work, apache+mod_wsgi works, django runserver works

For optional Jira ticketing interaction::

  $ pip install jira (or easy_install jira)

Setting up the environment for Servermon
----------------------------------------

Configuring database
++++++++++++++++++++

Note: servermon needs nothing more than the SELECT privelege. However
hwdoc needs also INSERT,UPDATE,DELETE and installation requires creating
tables etc. So a temporary GRANT ALL will be needed which later can be
dropped

Temporarily provide full access to the app::

  mysql> grant all privileges on puppet.* to 'servermon'@'example.com';

After installation is completed remember to revoke that::

  mysql> revoke all privileges on puppet.* from 'servermon'@'example.com';
  mysql> grant select on puppet.* to 'servermon'@'example.com';

If you intend to use hwdoc then you need to also::

  mysql> grant update,insert,delete on puppet.* to 'servermon'@'example.com';

If you follow a different procedure like installing servermon on a
separate db from Puppet the above instructions must be modified
accordingly (having servermon on a separate db could be useful if, for
example, you are replicating the puppet db from a master elsewhere).

Configuring app servers
+++++++++++++++++++++++

**Mandatory**.

Configure web server::

        TODO: To be written

If you are installing the software at the same VirtualHost with some other
software urls.py may need changes depending on the top url.

Setting up cron for package updates display
+++++++++++++++++++++++++++++++++++++++++++

You probably want the list of updatable packages to be updated with all
the new info. This needs a cron entry

This should probably tuned to each user's installation. Assuming an
installation in to /srv/servermon the following line is sufficient
in a crontab::

  0 0 * * * <user> /srv/servermon/manage.py make_updates --pythonpath=/srv/servermon

where user is a valid system user capable of reading (root will work,
but it is doubtfull it is a good choice. A dedicated user is probably
better)

Configuring settings.py
+++++++++++++++++++++++

**Mandatory**.

First you need to copy settings.py.dist::

  $ cp /path/to/servermon/
  $ cd servermon/servermon
  $ cp settings.py.dist settings.py

Then you need to configure the project. Things to pay attention to::

  DEBUG = False when in production
  DATABASES => Fill it with needed info
  TIME_ZONE => If you care about correct timestamps
  STATIC_URL => (static media directory)
  LDAP_AUTH_SETTINGS => if any
  TEMPLATE_DIRS => at least '/path/to/servermon/templates' needed
  INSTALLED_APPS => (uncomment needed apps). django admin apps are a must for hwdoc
  AUTHENTICATION_BACKENDS = > comment or uncomment
      'djangobackends.ldapBackend.ldapBackend',
      depending on whether you want LDAP user authentication or not

Create database tables
++++++++++++++++++++++
Create standard Django tables::

	./manage.py syncdb

to create all the necessary tables in the database.

Create application tables using south migrations::

	./manage.py migrate

Load initial data
+++++++++++++++++
Optionally load vendor and model data::

	./manage.py loaddata vendor-model

Test run
++++++++
Conduct a test run::

        ./manage.py runserver

And navigate to http://localhost:8000

Ticketing
+++++++++

Servermon allows for integration with ticketing systems. The idea is to
be able to easily search and  visualize equipments with open tickets.
This is accomplished through a 'caching' layer in the database, where
tickets are stored and their relationship to equipments. The system
allows for vendor specific plugins for each ticketing system. To select
you ticketing system edit settings.py and set::

  TICKETING_SYSTEM = 'dummy' # dummy, comments, jira are possible values

And then the configuration for you chosen ticketing system.

For the comments ticketing system a single. Tickets are assumed to have
URLs in the form COMMENTS_TICKETING_URL/ticket_id

In order to populate and update tickets a cron job running a django
command is needed. The idea is to run::

  $ ./manage.py hwdoc_populate_tickets ALL_EQS

This should probably tuned to each user's installation. Assuming an
installation in to /srv/servermon the following line might be
sufficient in a crontab::

  0 0 * * * <user> /srv/servermon/manage.py hwdoc_populate_tickets --pythonpath=/srv/servermon ALL_EQS

where user is a valid system user capable of reading (root will work,
but it is doubtfull it is a good choice. A dedicated user is probably
better)

Branding
++++++++

Inside the static folder you will find the standard django logo. Change it with
your organization's if you wish

Further steps
-------------

You can now proceed to accessing through a web browser either / for
viewing the Puppet frontend or /hwdoc for access to hwdoc fronted or
/admin for management
Via the admin interface, modify as required the existing (example.com) Site
instance. This is needed to point to the Virtual Host the application is
installed in for Opensearch to work

.. vim: set textwidth=72 :
.. Local Variables:
.. mode: rst
.. fill-column: 72
.. End:
