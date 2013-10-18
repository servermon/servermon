#!/usr/bin/env python
#
# Simply trigger Python Build Reasonableness
# https://pypi.python.org/pypi/pbr
# http://docs.openstack.org/developer/pbr/
#
# Actual configuration in setup.cfg

from setuptools import setup

setup(
    setup_requires=['pbr'],
    pbr=True,
)
