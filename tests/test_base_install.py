"""Core imports must work without the scientific packages in the test extra."""
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

import ontolutils
from ontolutils import Thing, namespaces, urirefs


def test_import_keeps_user_cache_out_of_module_search_path_and_defers_generation():
    result = subprocess.run(
        [sys.executable, '-I', '-c', '''
import importlib
import sys
sys.path.insert(0, sys.argv[1])
before = list(sys.path)
import ontolutils
from ontolutils import namespacelib
assert sys.path == before, 'Importing metadata models must not add a writable cache to sys.path'
assert 'ontolutils.namespacelib.__dev' not in sys.modules
assert str(namespacelib.QUDT_UNIT.M) == 'http://qudt.org/vocab/unit/M'
assert callable(namespacelib.__dev.generate_namespace_file_from_ttl)
assert namespacelib.__dev is importlib.import_module('ontolutils.namespacelib.__dev')
assert sys.path == before
''', str(Path(ontolutils.__file__).resolve().parent.parent)],
        capture_output=True, text=True, check=False, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr


def test_core_serialization_without_scientific_dependencies():
    result = subprocess.run(
        [sys.executable, "-I", "-c", '''
import importlib.abc
import sys

class NoScientificDependencies(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {"numpy", "pint", "xarray"}:
            raise ModuleNotFoundError(f"{fullname} is absent from a base install", name=fullname)

sys.meta_path.insert(0, NoScientificDependencies())
sys.path.insert(0, sys.argv[1])
from ontolutils import Thing
from ontolutils.arrays import to_xarray
from ontolutils.units import convert_value_qudt, to_pint
from rdflib import Graph, URIRef, RDF, OWL
thing = Thing(id="https://example.org/thing", label="Example")
graph = Graph().parse(data=thing.model_dump_jsonld(), format="json-ld")
assert (URIRef(thing.id), RDF.type, OWL.Thing) in graph
assert not {"numpy", "pint", "xarray"}.intersection(sys.modules)
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
