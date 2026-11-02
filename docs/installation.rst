.. _installation:

Installation
============

Use Python 3.9–3.14. A virtual environment keeps project dependencies separate.
After activating your environment, install:

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
   * - Numerical variables in ``ontolutils.ex.m4i``
     - ``numpy``
   * - Pint quantities and unit conversion
     - ``numpy pint``
   * - Numerical variables as xarray DataArrays
     - ``numpy pint xarray``
   * - SHACL graph validation
     - ``pyshacl``

For example:

.. code-block:: console

   python -m pip install numpy pint xarray
   python -m pip install pyshacl

Development installations use ``python -m pip install -e ".[test]"`` from a
source checkout. See :doc:`development` for tests and documentation builds.
