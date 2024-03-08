Developer documentation
=======================

.. _dev

Generate this documentation
---------------------------

The documentation is build based on this example
project: https://example-sphinx-basic.readthedocs.io/en/latest/index.html

All documentation documents are located in the `docs/` folder.

To generate the documentation, use the following commands:

.. code-block:: console

    # Install required Python dependencies (Sphinx etc.)
    pip install -r docs/requirements.txt

    # Enter the Sphinx project
    cd docs/

    # Run the raw sphinx-build command
    sphinx-build -M html . _build/