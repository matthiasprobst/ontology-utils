# Tests

Make sure you installed the package with the `test` extra:

```bash
pip install -e .[test]
```

## Running the tests
To test the package, you can run the following command in the terminal (from the root directory of the package):

```bash
pytest
```

This will run all the tests in the `tests` directory.

## Model and installed-wheel compatibility

The offline behavioral baseline checks validation errors, field names and aliases,
IRI references, typed literals, nested models and language tags. RDF output is
compared as graphs, including blank nodes, rather than by serializer whitespace
or prefix order:

```bash
python -m pytest tests/test_model_compatibility.py tests/test_base_install.py tests/test_download.py -q
```

The core package works without NumPy. The array-specific test skips when NumPy is
absent; install the `test` extra to exercise array serialization. Download tests
use fixed HTTP responses and temporary caches rather than live mutable files.

The `Installed compatibility` workflow builds an sdist and then a wheel from it.
It installs that wheel in clean environments with both the semantic dependency
floors in `tests/constraints/lowest.txt` and the newest versions permitted by the
package metadata and each Python interpreter. It covers Python 3.9 through 3.14
on Linux, with additional Python 3.12 checks on Windows and macOS. The separate
`Tests` workflow runs the full suite across all declared Python/OS combinations.
Install reports, resolved versions and JUnit results are retained as CI artifacts.
Pydantic 2.12.0 is the older-version baseline on Python 3.14; the other interpreters
use the declared 2.8.2 floor. RDFLib's floor is 7.0.0.

To reproduce the installed check, build with `python -m build`, create a fresh
virtual environment and install the resulting wheel together with `pytest` and
`packaging`. For the older dependency baseline, pass
`-c tests/constraints/lowest.txt` to that install command. Run from outside the
checkout, using absolute test paths:

```bash
python -I -m pytest --import-mode=importlib /path/to/ontology-utils/tests/test_dependency_contracts.py /path/to/ontology-utils/tests/test_model_compatibility.py /path/to/ontology-utils/tests/test_base_install.py -q
python -m pip check
python -m pip freeze
```

`-I` and `--import-mode=importlib` keep the source checkout off Python's import
path, so these checks exercise the installed candidate and its metadata.

## Consumer contracts

`tests/consumers/test_models.py` exercises a standard name from ssnolib and a
virtual camera with nested source code from pivmetalib. These tests cover aliases,
validation, expected RDF triples and model round trips with inline contexts.
They skip when their optional consumer is absent from a normal development
environment. The consumer CI job installs both pinned reference releases and
requires both imports before running the tests, so a missing consumer fails CI.

The consumer profile also installs NumPy because these reference releases import
`ontolutils.ex.m4i`. A base ontolutils wheel does not need that optional module.
Run the profile with:

```bash
python -m pip install -r tests/constraints/consumers.txt
python -I -c "import ssnolib, pivmetalib"
python -I -m pytest --import-mode=importlib tests/consumers -q
```

Install the candidate ontolutils wheel in the same environment first. Let the
resolver enforce the consumers' own stricter dependency bounds. These two model
contracts complement each consumer's full test suite; they do not establish
compatibility for every consumer feature or Python version.

## Documentation examples

`python -m pytest tests/test_documentation.py -q` executes the README and Antora
Python blocks and the tutorial notebook in temporary directories. The Sphinx
guide uses `.. testcode::` blocks checked by the doctest build. See
`docs/README.md` for its command, dependencies, and the editing workflow.

## Test coverage

To check the test coverage, you can run the following command in the terminal (from the root directory of the package):

```bash
pytest --cov=ontolutils --cov-report html
```

This will create a folder `htmlcov/` with an `index.html` file in it.

## Running pylint

To check the code style, you can run the following command in the terminal (from the root directory of the package):

```bash
pylint ontolutils --output=.pylint
```
