====================
Servermon 0.6 design
====================

This document describes the architecture of servermon in 0.6

.. contents:: :depth: 3

Objective
=========

Documenting the changes in design from 0.5 to 0.6

Background
==========

Servermon 0.5 supports Django 1.2, 1.3 and 1.4. However it is not very
adequate release anymore, since there are needs for a unified approach as far
as information visibility and search are concerned.

Overview
========

There have been multiple requests for a better look and feel and a more unified
approach to the data of the project's apps. This version should focus on
providing easy ways to move from one app to the other, better information
visibility and a unified search. Bootstrap might cover the better look and feel
requirements and a heavy restructuring of the apps would suffice for the second

Detailed design
===============


The will be no changes in models in any app. However views and templates will be 
heavily modified.

Changes per application

projectwide app
---------------

A project wide app has been introduced that will host all views and functions that
either don't belong anywhere else or should returns results from all other apps

hwdoc app
---------

Views and templates as well as urls that are project wide suchs as opensearch and 
suggestions will be moved to projectwide app. Easy transitions to other apps should
be implemented

updates app
-----------

Mostly left untouched. There might be a search function returing needed updates

puppet app
----------

Views and templates as well as urls that are project wide will be moved to projectwide
app. Search function will return all kinds of fact values. Easy transitions should be
implemented

