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
DCAT distribution downloads also use fixed responses and temporary destinations,
and run on every supported Python version.
JSON-LD ``@import`` model tests use temporary local context documents, including
an imported predicate alias. They check actual import resolution and model round
trips without depending on mutable upstream context files or network availability.
The stored PROV person fixture declares its required context terms inline.

The QUDT, Metadata4Ing and SOSA domain tests load `data/qudt_lookup.ttl` through
controlled graph loaders. This is a 290-triple excerpt of complete subject
descriptions from QUDT 3.1.9, attributed to QUDT.org under CC BY 4.0. The source
commit is `cf953bf42846f28c6b40a71a74763b2ab1d92069`. Before extraction, the unit
source SHA-256 was verified as
`a4c0f8b0585496faf3c1149047d5eaa906d2f1ac49cf4e98b9678e9fd4f89691`
and the quantity-kind source as
`376d0514a51e11048861626b691ac96a053824199ebf43ecb2856084e08cb082`.
These checks exercise lookup and model behavior offline. `test_qudt_sources.py`
checks the production downloader's checksum, timeout and HTTP-error contracts
using controlled HTTP responses. Live service availability requires a separate
network check.

The `Installed compatibility` workflow builds an sdist and then a wheel from it.
It installs that wheel in clean environments with both the semantic dependency
floors in `tests/constraints/lowest.txt` and the newest versions permitted by the
package metadata and each Python interpreter. It targets Python 3.11 through 3.15
on Linux, with additional Python 3.12 checks on Windows and macOS. The separate
`Tests` workflow runs the full suite across all declared Python/OS combinations.
Install reports, resolved versions and JUnit results are retained as CI artifacts.
Pydantic 2.12.0 is the older-version baseline on Python 3.14 and 2.14.0 on Python
3.15. Python 3.11–3.13 use the declared 2.8.2 floor. RDFLib's floor is 7.0.0.

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
environment. For the 1.0 major release, downstream repositories migrate
separately; these historical contracts are not a release CI gate. Update them
alongside consumer migrations before treating them as current compatibility
evidence. Require both imports when claiming that a consumer profile passed.

The consumer profile also installs NumPy because these reference releases import
`ontolutils.ex.m4i`. Those models are absent from the 1.0 wheel. The repository keeps model definitions in `tests/ontology_fixtures` for RDF regression tests.
For historical 0.27 investigations, run the profile with:

```bash
python -m pip install -r tests/constraints/consumers.txt
python -I -c "import ssnolib, pivmetalib"
python -I -m pytest --import-mode=importlib tests/consumers -q
```

These pinned releases exclude ontolutils 1.0 and cannot validate its candidate.
When testing migrated consumers, install the candidate wheel in the same
environment and let the resolver enforce their dependency bounds. These two model
contracts complement each consumer's full test suite; they do not establish
compatibility for every consumer feature or Python version.

## Documentation examples

`python -m pytest tests/test_documentation.py -q` executes the README and Antora
Python blocks and the tutorial notebook in temporary directories. The Sphinx
guide uses `.. testcode::` blocks checked by the doctest build. See
`docs/README.md` for its command, dependencies, and the editing workflow.

## Publisher vocabulary snapshots

Run the publisher-source check from the repository root:

```bash
python -m scripts.verify_publisher_namespaces .work/publisher-namespaces --download
```

The check verifies SHA-256 before parsing, regenerates after reversing triple
insertion order, and checks every rendered IRI. Omit `--download` to verify
the same local files offline. Preserve the verified files if a publisher URL
can serve a newer revision. The command reports differences from the bundled
namespace so you can review them before adopting a generated module. It checks
RDF terms and leaves project-specific Python aliases and models to the project.

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
