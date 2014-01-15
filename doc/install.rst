Servermon installation tutorial
===============================

Documents Servermon version 0.6.1

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
2) hwodc: A simple datacenter hardware documentation database

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

Python, Django, South is needed::

  $ aptitude install python-django
  $ aptitude install python-django-south
  $ aptitude install python-whoosh
  $ aptitude install python-ipy
  $ aptitude install python-mysqldb (or sqlite or psycopg2)
  $ aptitude install python-ldap (for user authentication via LDAP)
  $ mkdir /path/to/servermon
  $ tar xfvz servermon-X.Y.tar.gz -C /path/to/servermon

A Puppet infrastructure with an RDBMS (MySQL, PostgreSQL) is needed for
everything else apart from hwdoc

An application server. Gunicorn should work, apache+mod_wsgi works, django runserver works

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

If you intend to also use hwdoc then you need to also::
  mysql> grant update,insert,delete on puppet.* to 'servermon'@'example.com';

Configuring urls.py
+++++++++++++++++++

**Mandatory**.

Configure web server::

        TODO: To be written

For most cases a::

  $ cd /path/to/servermon
  $ cp urls.py.dist urls.py

should be sufficient. However if you are installing the software at the
same VirtualHost with some other software the above file may need
changes depending on the top url.

Configuring settings.py
+++++++++++++++++++++++

**Mandatory**.

First you need to copy settings.py.dist::

  $ cp /path/to/servermon
  $ cp settings.py.dist settings.py

Then you need to configure the project. Things to pay attention to::

  DEBUG = False when in production
  DATABASES => Fill it with needed info
  TIME_ZONE => If you care about correct timestamps
  MEDIA_URL => Pretty self explanatory
  STATIC_URL => (static media directory)
  LDAP_AUTH_SETTINGS => if any
  TEMPLATE_DIRS => at least '/path/to/servermon/templates' needed
  INSTALLED_APPS => (uncomment needed apps). django admin apps are a must for hwdoc
  AUTHENTICATION_BACKENDS = > comment or uncomment
      'servermon.djangobackends.ldapBackend.ldapBackend',
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
