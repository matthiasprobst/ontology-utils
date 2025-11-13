import logging
import unittest

import rdflib

from ontolutils import Thing
from ontolutils import serialize
from ontolutils.ex import hdf5
from ontolutils.ex import m4i

LOG_LEVEL = logging.DEBUG

_QUERY = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?s
WHERE {
    ?s a  owl:Thing.
}
"""


class TestSerialization(unittest.TestCase):

    def test_jsonld(self):
        thing = Thing(id="https://example.com/123")
        json_ld: str = thing.model_dump_jsonld()
        g = rdflib.Graph()
        g.parse(data=json_ld, format='json-ld')
        res = g.query(_QUERY)
        bindings = res.bindings[0]
        self.assertEqual(bindings[rdflib.Variable("s")], rdflib.URIRef("https://example.com/123"))

    def test_ttl(self):
        thing = Thing(id="https://example.com/123")
        serialized: str = thing.serialize(format='ttl', base_uri="https://example.com/")
        expected_serialization = """@prefix owl: <http://www.w3.org/2002/07/owl#> .

<https://example.com/123> a owl:Thing .

"""
        self.assertEqual(serialized, expected_serialization)

        g = rdflib.Graph()
        g.parse(data=serialized, format='ttl')
        res = g.query(_QUERY)
        bindings = res.bindings[0]
        self.assertEqual(bindings[rdflib.Variable("s")], rdflib.URIRef("https://example.com/123"))

    def test_n3(self):
        thing = Thing(id="https://example.com/123")
        serialized: str = thing.serialize(format='n3', base_uri="https://example.com/")
        expected_serialization = """@prefix owl: <http://www.w3.org/2002/07/owl#> .

<https://example.com/123> a owl:Thing .

"""
        self.assertEqual(serialized, expected_serialization)
        g = rdflib.Graph()
        g.parse(data=serialized, format='n3')
        res = g.query(_QUERY)
        bindings = res.bindings[0]
        self.assertEqual(bindings[rdflib.Variable("s")], rdflib.URIRef("https://example.com/123"))

    def test_serialize_mutliple_things(self):
        thing1 = m4i.Tool(
            id="http://example.org/tool1",
            label="Tool"
        )
        thing2 = hdf5.Dataset(
            id="http://example.org/tool1",
            name="/ds"
        )
        self.assertEqual(serialize([thing1, thing2], "ttl"), """@prefix hdf5: <http://purl.allotrope.org/ontologies/hdf5/1.8#> .
@prefix m4i: <http://w3id.org/nfdi4ing/metadata4ing#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/tool1> a hdf5:Dataset,
        m4i:Tool ;
    rdfs:label "Tool" ;
    hdf5:name "/ds" .

""")
