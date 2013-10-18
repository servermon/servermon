servermon
=========

Servermon is a Django project with the aim of facilitating server monitoring
and management through Puppet.

Install
=======

Get the python modules:

  pip install -r requirements.txt

Copy servermon/settings.py.dist to servermon/settings.py

See doc/install.rst for details.

    ./manage.py syncdb
    ./manage.py migrate

Run!
    ./manage.py runserver
