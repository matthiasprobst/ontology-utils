"""Run the examples readers copy, including the notebook from a fresh session."""
import json
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_PYTHON = re.compile(r"^```python\s*\n(.*?)^```\s*$", re.M | re.S)
ASCIIDOC_PYTHON = re.compile(r"^\[source,python\]\s*\n----\s*\n(.*?)^----\s*$", re.M | re.S)


def python_blocks(path):
    text = path.read_text(encoding="utf-8")
    pattern = MARKDOWN_PYTHON if path.suffix == ".md" else ASCIIDOC_PYTHON
    return [(text[:match.start(1)].count("\n"), match.group(1)) for match in pattern.finditer(text)]


EXAMPLE_PAGES = [ROOT / "README.md"] + sorted((ROOT / "antora/modules").rglob("*.adoc"))
EXAMPLE_PAGES = [page for page in EXAMPLE_PAGES if python_blocks(page)]


@pytest.mark.parametrize("page", EXAMPLE_PAGES, ids=lambda path: path.relative_to(ROOT).as_posix())
def test_documented_python_examples(page, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    namespace = {"__name__": "__main__"}
    for line_offset, source in python_blocks(page):
        exec(compile("\n" * line_offset + source, str(page), "exec"), namespace)


def test_tutorial_runs_in_cell_order(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    path = ROOT / "tutorials/Classes.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    assert notebook["cells"][0]["cell_type"] == "markdown"
    namespace = {"__name__": "__main__"}
    executed = 0
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] == "code":
            source = "".join(cell["source"])
            if source.strip():
                exec(compile(source, f"{path}:cell-{index}", "exec"), namespace)
                executed += 1
    assert executed > 0
