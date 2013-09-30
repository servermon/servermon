====================
Servermon 0.7 design
====================

This document describes the architectural changes of servermon in 0.7

.. contents:: :depth: 3

Objective
=========

Documenting the changes in design from 0.6 to 0.7

Background
==========

Servermon 0.6 supports Django 1.2, 1.3 and 1.4. After the successfull
unification of the search functions as well as the better information
dissipation throughout the interface it is high time various useful
features are added to the project. Focus will be the hwdoc app but minor
changes will probably find their way in the other applications

Overview
========

There have been requests for various additions to hwdoc. These ideas include
(but are not limited to):
 * Patch panel support
 * PDU (0U support would be great)
 * Front/back/middle parts of the rack
 * AC (rack models
 * InDC interim storage capabilities
 * Outside DC storage capabilities
 * Statistics in a pleasing visual form (graphs, pies, bars)
 * Making the overview pages more informative
 * Granular permission scheme (e.g. guest access, with serial numbers and other
   sensitive information hidden)
 * Generic key/value store & tags for equipment (e.g. to allow asset tags to be
   entered)
 * Allow devices not owned by servermon admin to be added (e.g. missing serials)
 * Prettify rack view
 * Add better rack selection (accounting for rows) & stencils.
 * Data center floor plans & rack positions
 * Decouple comments from ticketing systems
 * Racktables importer

Most require adding to the hwdoc app's models, statistics require some javascript
graphing library (tests with flot are being conducted) and the corresponding JSON-
returning views

Detailed design
===============

There will be changes in models of hwdoc app at least. Multiple new models and
views as well as templates will have to be added

Changes per application

projectwide app
---------------

Some changes in the overview page will take place to facilitate easy viewing of
statistics

hwdoc app
---------

Ticketing support
+++++++++++++++++

A Ticket model is to be added with a foreign (or multiforeign) key to equipment
in order to store "open" tickets tied with an equipemt. The information in that
models is to be minimal (ticket ID (char), link to ticket(char)) in order to
avoid forcing assumptions on the ticketing system.
 
A django management command to populate the table as well as the relationships
will be provided. This django management command should have a pluggable
architecture to allow different ticketing systems to be used through the use
of plugins

InRow AC
++++++++

InRow AC can be supported by adding a single attribute is_inrow_ac to RackModel.
RackModel is already capable of storing any kind of Rack like inRow AC but the
extra functionality they might provide is not reflected somehow. After that
some basic displaying can be achieved through stencils or standard html tables.

updates app
-----------

Expected to be left untouched.

puppet app
----------

Expected to be left untouched.
