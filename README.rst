========================
Team and repository tags
========================

.. image:: http://governance.openstack.org/badges/horizon-cisco-ui.svg
    :target: http://governance.openstack.org/reference/tags/index.html

.. Change things from this point on

===============================================================
Cisco UI: Cisco Extension for the OpenStack Dashboard (Horizon)
===============================================================

* Release management: https://launchpad.net/horizon-cisco-ui
* Blueprints and feature specifications: https://blueprints.launchpad.net/horizon-cisco-ui
* Issue tracking: https://bugs.launchpad.net/horizon-cisco-ui

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

Building Documentation
======================

This documentation is written by contributors, for contributors.

The source is maintained in the ``doc/source`` directory using
`reStructuredText`_ and built by `Sphinx`_

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx-doc.org/

* Building Automatically::

    $ ./run_tests.sh --docs

* Building Manually::

    $ tools/with_venv.sh sphinx-build doc/source doc/build/html

Results are in the ``doc/build/html`` directory
