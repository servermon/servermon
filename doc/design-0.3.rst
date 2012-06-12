====================
Servermon 0.3 design
====================

This document describes the architecture of servermon in 0.3. The only
subapp that will be documented is hwdoc at this point.

.. contents:: :depth: 3

Objective
=========

Servermon 0.3 hwdoc is an application to facilitate documenting
equipment attributes and allocations

Background
==========

Servermon 0.2 was the first version that had basic hwdoc functionality.
It also had many bugs, no documentation and few ways of testing. 0.3
version's driving concept was to create a more stable version with
adequate documentation, better QA while also providing various fixes and
new functionality without API or ABI breakage

Overview
========

hwdoc in 0.3 has some basic models for storing equipment information and
relations corresponding django views and templates

Detailed design
===============

The models in hwdoc can be split in 2 categories. Equipment related
models and allocation related models

Equipment models
----------------

Equipment related models are the equipment itself holding info such as
location, size, serials, vendor, mode, remote management possibilities
etc

Allocation models
-----------------

Allocation are used to assign an equipment to a generic entity called
Project comprised of multiple individuals and their roles in it. The
idea is to have a place for contact points and in case the tool is used
in procedures for exclusive locking in equipment

Logging
-------

The logging system will be switched completely to the standard python
logging module. That however has been chose to become dependent on
Django version so implementation will stall for a while
