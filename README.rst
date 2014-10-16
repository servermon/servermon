servermon
=========

.. image:: https://travis-ci.org/servermon/servermon.svg?branch=master
    :target: https://travis-ci.org/servermon/servermon
    :alt: Build Status

.. image:: https://readthedocs.org/projects/servermon/badge/?version=latest
    :target: https://readthedocs.org/projects/servermon/?badge=latest
    :alt: Documentation Status

Servermon is a Django project with the aim of facilitating server monitoring
and management through Puppet.

Servermon at this point offers two applications

1) A Web frontend to the Puppet database.
2) hwdoc: A simple datacenter hardware documentation database

If you have no idea what Puppet is, it is possible that you don't need
this software. Do note however that hwdoc will still be usable even
without a Puppet infrastructure

Compatibility
=============

As of October 2013, we mosty support Django 1.4. Django 1.5 or later is NOT
supported.

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

More details in the `installation tutorial <https://servermon.readthedocs.org/en/latest/install.html>`_.

Documentation
=============

The documentation is maintained using Sphinx (under /doc/) and is automatically
generated at https://servermon.readthedocs.org/.
