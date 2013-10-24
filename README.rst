servermon
=========

Servermon is a Django project with the aim of facilitating server monitoring
and management through Puppet.

Install
=======

Get the python modules:

.. code-block:: bash

  pip install -r requirements.txt

Copy servermon/settings.py.dist to servermon/settings.py

See doc/install.rst for details.

.. code-block:: bash

    ./manage.py syncdb
    ./manage.py migrate

Run!

.. code-block:: bash

    ./manage.py runserver

Documentation
=============

The documentation is maintained using Sphinx (under /doc/) and is automatically
generated at https://servermon.readthedocs.org/.
