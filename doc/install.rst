Servermon installation tutorial
===============================

Documents Servermon version |version|

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

If you have no idea what Puppet is, it is possible that you don't need
this software. Do note however that hwdoc will still be usable even
without a Puppet infrastructure

Installation
------------

Hardware requirements
+++++++++++++++++++++

Any system supported by your Linux distribution is fine. 64-bit systems
are the ones tested better but there is no reason 32-bit systems should
not work 

Installing the software
+++++++++++++++++++++++

**Mandatory**.

Python, Django, South is needed::

  $ aptitude install python-django
  $ aptitude install python-south
  $ mkdir /path/to/servermon
  $ tar xfvz servermon-X.Y.tar.gz -C /path/to/servermon

A Puppet infrastructure with an RDBMS (MySQL, PostgreSQL) is needed for
everything else apart from hwdoc

Setting up the environment for Servermon
----------------------------------------

Configuring urls.py
+++++++++++++++++++

**Mandatory**.

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
  LDAP_AUTH_SETTINGS => if any
  TEMPLATE_DIRS => at least '/path/to/servermon/templates' needed
  INSTALLED_APPS => Probaly you can uncomment all

Further steps
-------------

You can now proceed to either / for viewing the Puppet frontend or
/hwdoc for access to hwdoc fronted or /admin for management

.. vim: set textwidth=72 :
.. Local Variables:
.. mode: rst
.. fill-column: 72
.. End:
