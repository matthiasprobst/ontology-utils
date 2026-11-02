Development and documentation
=============================

From a source checkout, install the test dependencies and run the suite:

.. code-block:: console

   python -m pip install -e ".[test]"
   python -m pytest --cov --cov-report=xml

``tests/README.md`` describes installed-wheel checks, older/newer semantic
dependencies, and representative consumer models. Inspect their results before
changing compatibility bounds.

Build and check the documentation
----------------------------------

Read the Docs uses ``.readthedocs.yaml`` and ``docs/conf.py``. Install the package
and Sphinx tools together. NumPy and pyshacl are needed to execute the numerical
variable and SHACL examples:

.. code-block:: console

   python -m pip install . -r docs/requirements.txt numpy pyshacl
   python -m pip check
   python -m sphinx -W --keep-going -b html docs docs/_build/html
   python -m sphinx -W --keep-going -b doctest docs docs/_build/doctest
   python -m pytest tests/test_documentation.py -q

The HTML build checks references and formatting. The doctest build executes the
guide examples, including their assertions; pytest checks the README, Antora
Python examples, and the notebook from a fresh session. The save/load doctests
write example files in the invocation's working directory. Use a scratch
directory and absolute paths when needed.

Documentation tool ranges live in ``docs/requirements.in`` and are included by
``docs/requirements.txt``. Runtime dependencies come from ``pyproject.toml``.
Record ``python -m pip freeze`` when diagnosing a specific build; these ranges
are not a frozen environment. See ``docs/README.md`` for editing guidance.
