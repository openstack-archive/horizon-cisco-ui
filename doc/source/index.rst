===============================================================
Cisco UI: Cisco Extension for the OpenStack Dashboard (Horizon)
===============================================================

Introduction
============

Cisco UI is a Horizon Dashboard for interacting with Cisco Systems hardware.
It uses the standard Horizon extension systems, and maintains code and styling
consistency where possible.

Most of the developer information, as well as an overview of Horizon, can be
found in the `Horizon documentation online`_.

.. _Horizon documentation online: http://docs.openstack.org/developer/horizon/index.html

Getting Started
===============

The quickest way to get up and running is:

  1. Setup a basic `Devstack installation`_
  2. Clone `Cisco UI`_ with ``git clone https://github.com/openstack/horizon-cisco-ui``
  3. Enter the ``horizon-cisco-ui`` directory, and run ``./dev_install.sh``.
     Follow the on screen instructions. Often the default settings will be
     adequate, so you can just hit enter twice.

.. _Devstack installation: http://docs.openstack.org/developer/devstack/
.. _Cisco UI: https://github.com/openstack/horizon-cisco-ui

Contributing
============

File `bugs`_ and `blueprints`_ on Launchpad, as with other OpenStack projects.

Use the existing `Horizon blueprint template`_ when adding blueprints. This
helps with consistency.

.. _bugs: https://bugs.launchpad.net/horizon-cisco-ui/
.. _blueprints: https://blueprints.launchpad.net/horizon-cisco-ui/
.. _Horizon blueprint template: https://blueprints.launchpad.net/horizon/+spec/template

Release Notes
=============

.. toctree::
  :glob:
  :maxdepth: 1

  releases/*

Source Code Reference
=====================

.. toctree::
  :glob:
  :maxdepth: 1

  sourcecode/autoindex


