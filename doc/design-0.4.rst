====================
Servermon 0.4 design
====================

This document describes the architecture of servermon in 0.4

.. contents:: :depth: 3

Objective
=========

Documenting the changes in design from 0.3 to 0.4

Background
==========

Servermon 0.2 was the first version that had basic hwdoc functionality.
It also had many bugs, no documentation and few ways of testing. 0.3
version's driving concept was to create a more stable version with
adequate documentation, better QA while also providing various fixes and
new functionality without API or ABI breakage. With 0.3 having achieved most
of the above goals 0.4 was due to be an improvement in hwdoc's support for 
Racks and Datacenters. However a lot of changes have happened in servermon as
well, mostly due to performance improvents patches submitted by Faidon Liambotis

Overview
========

hwdoc in 0.4 has some basic models for storing Racks, RackRows and Datacenters.
A lot of patches for performance improvements have been submitted in servermon

Detailed design
===============

The new models in hwdoc are mostly about Rack and their place in Datacenters

Rack models
-----------

Rack related models are used to store information about a rack, such as max,min
mounted depth, actual mounted depth. Equipment is stored directly in a Rack in
a specific unit

Dataceter models
----------------

Datacenter models include Datacenter and RackRow. The idea is to document
Racks' positions in RackRows and RackRows positions in Datacenter.
