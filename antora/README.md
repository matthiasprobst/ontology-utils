# Antora draft

The published documentation uses Sphinx (`docs/` and `.readthedocs.yaml`).
This directory is an alternate Antora draft covering the same implementation.
Its Python examples are checked by `tests/test_documentation.py`.

Antora requires Node.js and its CLI/site generator; `pip install antora` is
not the documented installation route. See the
[official Antora setup guide](https://docs.antora.org/antora/3.1/install/install-antora/).
With the CLI and generator installed, run from this directory:

```console
antora antora-playbook.yml
```

On Windows PowerShell, use `antora.cmd` if the `.ps1` launcher is blocked.

The playbook reads `../` at `HEAD`, with `antora` as the component start path.
Local content comes from the working tree; its descriptor, navigation files,
and pages must be present. The UI bundle is `antora/ui-bundle.zip`; the `./`
prefix makes its path relative to the playbook. The current `output.dir: build`
uses the invocation's working directory. Inspect the generated `build/` locally;
this does not publish a site. The older `antora/docs/` copy is not a content root.

For the supported documentation build and executable examples, use
[the Sphinx instructions](../docs/README.md).
