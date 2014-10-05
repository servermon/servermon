Servermon upgrade procedures 
============================

.. contents::

Introduction
------------

Read the following for instructions on how to upgrade between versions

Please note that only upgrade paths for consecutive versions have been tested.
Upgrade from 0.1 to 0.3 for example may or may not work.

Maintenance
-----------

It is possible to use a maintenace page instead of stopping the
application server in case you want to. A sample maintenance page is
provided in /static/maintenance.html but feel free to create your own.

Depending on your application server, different configuration steps will
be required. All in all, stopping all requests to the application and
presenting your maintenance page should be enough. Sample configuration
stanzas are provided below

Apache+wsgi
+++++++++++
TODO

Apache+mod_proxy
++++++++++++++++
TODO

Gunicorn
++++++++
No can do, you should have a reverse proxy in front anyway in which case
look at the apache config above

uwsgi
+++++
No can do, you should have a reverse proxy in front anyway in which case
look at the apache config above

Django runserver
++++++++++++++++
No can do, please tell me you are not running in production with the
development server

Upgrading from 0.6.1 to 0.7.0
-----------------------------
You should perform the following

* Stop application server (wsgi, gunicorn, etc)
* Update the make_updates.py cron to point to the new django management
  command. Look into the installation instructions on how to set it up
* Untar new version (backup the old one first) on top of the old one
* Restart application server (wsgi, gunicorn, etc)

Upgrading from 0.6.0 to 0.6.1
-----------------------------
You should perform the following

* Stop application server (wsgi, gunicorn, etc)
* Untar new version (backup the old one first) on top of the old one
* Restart application server (wsgi, gunicorn, etc)

Upgrading from 0.5.0 to 0.6.0
-----------------------------
You should perform the following

* Stop application server (wsgi, gunicorn, etc)
* Untar new version (backup the old one first). Note: Clean untar for
  this version is needed!!!!
* Merge urls.py with new urls.py.dist
* Merge settings.py with new settings.py.dist
* Migrate using south::

  $ ./manage.py migrate

* Restart application server (wsgi, gunicorn, etc)

Upgrading from 0.4.2 to 0.5.0
-----------------------------
You should perform the following

* Stop application server (wsgi, gunicorn, etc)
* Untar new version (backup the old one first). Note: Clean untar for
  this version is needed if upgrading from < 0.4.2
* Merge settings.py with new settings.py.dist
* Restart application server (wsgi, gunicorn, etc)

Upgrading from 0.4.1 to 0.4.2
-----------------------------
You should perform the following

* Stop application server (wsgi, gunicorn, etc)
* Untar new version (backup the old one first). Note: Clean untar for
  this version is needed
* Merge urls.py with new urls.py.dist
* Merge settings.py with new settings.py.dist
* Migrate using south::

  $ ./manage.py migrate

* Restart application server (wsgi, gunicorn, etc)


Upgrading from 0.4 to 0.4.1
---------------------------
You should perform the following

* Untar new version (backup the old one first)
* Restart application server (wsgi, gunicorn, etc)

Upgrading from 0.3 to 0.4
-------------------------
You should perform the following

* Untar new version (backup the old one first)
* Merge urls.py with new urls.py.dist
* Merge settings.py with new settings.py.dist
* Migrate using south::

  $ ./manage.py migrate updates 0001 --fake
  $ ./manage.py migrate

* Restart application server (wsgi, gunicorn, etc)

Upgrading from 0.2 to 0.3
-------------------------
You should perform the following

* Untar new version (backup the old one first)
* Merge urls.py with new urls.py.dist
* Merge settings.py with new settings.py.dist
* Migrate using south::

  $ ./manage.py migrate hwdoc

* Restart application server (wsgi, gunicorn, etc)

Upgrading from 0.1 to 0.2
-------------------------
In order to upgrade from 0.1 to 0.2 you should perform the following

* Install prerequisites: 

 * south (For debian based distros aptitude install python-django-south)
 * whoosh (For debian based distros aptitude install python-whoosh)

* Untar new version (backup the old one first)
* Merge urls.py with new urls.py.dist
* Merge settings.py with new settings.py.dist
* Migrate using south
	./manage.py migrate hwdoc 0001_initial --fake
	./manage.py migrate hwdoc

* Restart application server (wsgi, gunicorn, etc)

.. vim: set textwidth=72 :
.. Local Variables:
.. mode: rst
.. fill-column: 72
.. End:
