Servermon upgrade procedures 
============================

.. contents::

Introduction
------------

Read the following for instructions on how to upgrade between versions

Please note that only upgrade paths for consecutive versions have been tested.
Upgrade from 0.1 to 0.3 for example may or may not work.

Upgrading from 0.4.1 to 0.4.2
=========================
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
=========================
You should perform the following

* Untar new version (backup the old one first)
* Restart application server (wsgi, gunicorn, etc)

Upgrading from 0.3 to 0.4
=========================
You should perform the following

* Untar new version (backup the old one first)
* Merge urls.py with new urls.py.dist
* Merge settings.py with new settings.py.dist
* Migrate using south::

  $ ./manage.py migrate updates 0001 --fake
  $ ./manage.py migrate

* Restart application server (wsgi, gunicorn, etc)

Upgrading from 0.2 to 0.3
=========================
You should perform the following

* Untar new version (backup the old one first)
* Merge urls.py with new urls.py.dist
* Merge settings.py with new settings.py.dist
* Migrate using south::

  $ ./manage.py migrate hwdoc

* Restart application server (wsgi, gunicorn, etc)

Upgrading from 0.1 to 0.2
=========================
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
