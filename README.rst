====================================================
Cisco Extension for the OpenStack Dashboard (Horizon)
====================================================

* Release management: https://launchpad.net/horizon-cisco-ui
* Blueprints and feature specifications: https://blueprints.launchpad.net/horizon-cisco-ui
* Issue tracking: https://bugs.launchpad.net/horizon-cisco-ui

See ``doc/source/topics/install.rst`` about how to install the Cisco UI
in your OpenStack setup.

It is also available at http://docs.openstack.org/developer/horizon-cisco-ui/topics/install.html.

Getting Started for Developers
==============================

Run ``./dev_install.sh`` from the horizon-cisco-ui directory.

Building Contributor Documentation
==================================

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
