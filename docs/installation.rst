.. _installation:

Installation
============

This version supports Python 3.11–3.15. A virtual environment keeps
project dependencies separate. Python 3.14 needs Pydantic 2.12 or newer;
Python 3.15 needs Pydantic 2.14 or newer. The package declares these bounds so
dependency resolution cannot select an unsupported Pydantic floor.
Python 3.10 and earlier are not supported. A default PyPI installation may
select a stable release with a different API and Python range.

To follow this guide, start from the 1.0.0b1 source checkout and create an
isolated environment with a supported Python interpreter:

.. code-block:: console

   python --version
   python -m venv .venv

Activate it with ``. .\.venv\Scripts\Activate.ps1`` in PowerShell or
``source .venv/bin/activate`` on Linux/macOS. Then install from the checkout:

.. code-block:: console

   python -m pip install .
   python -m pip check

To use the latest published release instead:

.. code-block:: console

   python -m pip install ontolutils
   python -c "import ontolutils; print(ontolutils.__version__)"

The package installs its core dependencies, including Pydantic 2.x and RDFLib
7.x. You do not need to install them separately.

Optional tools
--------------

Install only the tools needed for your workflow:

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Feature
     - Additional packages
   * - Pint quantities
     - ``pint``
   * - Numerical data as xarray DataArrays
     - ``xarray`` and ``pint`` when formatting a QUDT unit
   * - SHACL graph validation
     - ``pyshacl``

For example:

.. code-block:: console

   python -m pip install pint xarray
   python -m pip install pyshacl

Development installations use ``python -m pip install -e ".[test]"`` from a
source checkout. See :doc:`development` for tests and documentation builds.
