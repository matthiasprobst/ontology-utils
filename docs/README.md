# Documentation

Sphinx is the published documentation; `.readthedocs.yaml` selects `docs/conf.py`.
The Antora tree is an alternate draft, with its own [build notes](../antora/README.md).

From the repository root, install the package and documentation tools together:

```console
python -m pip install . -r docs/requirements.txt
python -m pip check
python -m sphinx -W --keep-going -b html docs docs/_build/html
```

Open `docs/_build/html/index.html`. `requirements.txt` includes the Sphinx/theme
ranges in `requirements.in`; runtime dependencies come from `pyproject.toml`.

## Check examples before editing or publishing

Use `.. testcode::` for runnable guide examples. Blocks on one page run in order
in the same namespace; start each page with its own imports. Assertions should
check scientific values or RDF triples, not serializer whitespace. The SHACL and
numerical-variable examples additionally need `pyshacl` and `numpy`:

```console
python -m pip install numpy pyshacl
python -m sphinx -W --keep-going -b doctest docs docs/_build/doctest
python -m pytest tests/test_documentation.py -q
```

The doctest build checks the Sphinx guide; pytest executes the README, Antora
Python blocks, and tutorial notebook in temporary working directories. Install
the `test` extra when running pytest. The doctest save/load examples write
`person.jsonld` and `person.ttl` in the invocation's working directory, so use
a scratch directory and absolute source/output paths if you want to keep the
checkout free of example data.

The API pages read signatures and docstrings from the installed package. Reinstall
the checkout after changing them. Keep the curated `Thing` reference focused on
RDF methods rather than inherited Pydantic internals. Use task-oriented examples
in the guide and keep generated method pages out of manual edits.
