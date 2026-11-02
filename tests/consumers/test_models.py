"""Representative consumer contracts; CI installs both consumers explicitly."""
from importlib.util import find_spec

import pytest
from pydantic import ValidationError
from rdflib import Graph
from rdflib.compare import isomorphic

from ontolutils import QUDT_UNIT
from ontolutils.ex.schema import SoftwareSourceCode


def test_ssnolib_aliases_validation_and_graph_round_trip():
    if find_spec("ssnolib") is None:
        pytest.skip("ssnolib is not installed")
    import ssnolib
    standard_name = ssnolib.StandardName(
        id="https://example.org/x_velocity", standard_name="x_velocity",
        unit="m/s", description="Velocity along the x axis@en",
    )
    assert standard_name.standardName == standard_name.standard_name == "x_velocity"
    assert standard_name.unit == str(QUDT_UNIT.M_PER_SEC)
    with pytest.raises(ValidationError):
        ssnolib.StandardName(standard_name="invalid name", unit="m/s")

    expected = Graph().parse(data='''
        @prefix ssno: <https://matthiasprobst.github.io/ssno#> .
        <https://example.org/x_velocity> a ssno:StandardName ;
            ssno:standardName "x_velocity" ;
            ssno:unit <http://qudt.org/vocab/unit/M-PER-SEC> ;
            ssno:description "Velocity along the x axis"@en .
    ''', format="turtle")
    data = standard_name.model_dump_jsonld()
    assert isomorphic(Graph().parse(data=data, format="json-ld"), expected)
    restored = ssnolib.StandardName.from_jsonld(data=data, limit=1)
    assert restored.standard_name == "x_velocity"
    assert isomorphic(Graph().parse(data=restored.serialize("ttl"), format="ttl"), expected)


def test_pivmetalib_nested_source_code_alias_and_graph_round_trip():
    if find_spec("pivmetalib") is None:
        pytest.skip("pivmetalib is not installed")
    from pivmetalib.pivmeta.tool import VirtualCamera

    camera = VirtualCamera(
        id="https://example.org/camera", fnumber=4,
        source_code=SoftwareSourceCode(id="https://example.org/code", name="Camera simulator"),
    )
    assert camera.fnumber == "4"
    assert camera.source_code is camera.hasSourceCode
    expected = Graph().parse(data='''
        @prefix piv: <https://matthiasprobst.github.io/pivmeta#> .
        @prefix schema: <https://schema.org/> .
        @prefix codemeta: <https://codemeta.github.io/terms/> .
        <https://example.org/camera> a piv:VirtualCamera ; piv:fnumber "4" ;
            codemeta:hasSourceCode <https://example.org/code> .
        <https://example.org/code> a schema:SoftwareSourceCode ; schema:name "Camera simulator" .
    ''', format="turtle")
    data = camera.model_dump_jsonld()
    assert isomorphic(Graph().parse(data=data, format="json-ld"), expected)
    restored = VirtualCamera.from_jsonld(data=data, limit=1)
    assert isinstance(restored.hasSourceCode, SoftwareSourceCode)
    assert isomorphic(Graph().parse(data=restored.serialize("ttl"), format="ttl"), expected)
