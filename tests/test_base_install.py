"""Core imports must work without the scientific packages in the test extra."""
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

import ontolutils
from ontolutils import Thing, namespaces, urirefs


def test_core_serialization_without_numpy():
    result = subprocess.run(
        [sys.executable, "-I", "-c", '''
import importlib.abc
import sys

class NoNumpy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "numpy" or fullname.startswith("numpy."):
            raise ModuleNotFoundError("NumPy is absent from a base install", name="numpy")

sys.meta_path.insert(0, NoNumpy())
sys.path.insert(0, sys.argv[1])
from ontolutils import Thing
from rdflib import Graph, URIRef, RDF, OWL
thing = Thing(id="https://example.org/thing", label="Example")
graph = Graph().parse(data=thing.model_dump_jsonld(), format="json-ld")
assert (URIRef(thing.id), RDF.type, OWL.Thing) in graph
assert "numpy" not in sys.modules
''', str(Path(ontolutils.__file__).resolve().parent.parent)],
        capture_output=True, text=True, check=False, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_numpy_arrays_still_serialize_when_installed():
    np = pytest.importorskip("numpy")

    @namespaces(ex="https://example.org/")
    @urirefs(Samples="ex:Samples", values="ex:values")
    class Samples(Thing):
        values: Any

    samples = Samples(id="https://example.org/samples", values=np.array([1, 2, 3]))
    assert samples.get_jsonld_dict()["ex:values"] == [1, 2, 3]
