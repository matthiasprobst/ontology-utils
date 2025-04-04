import logging
import unittest

import rdflib

from ontolutils import Thing

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
        print(json_ld)
        g = rdflib.Graph()
        g.parse(data=json_ld, format='json-ld')
        res = g.query(_QUERY)
        bindings = res.bindings[0]
        self.assertEqual(bindings[rdflib.Variable("s")], rdflib.URIRef("https://example.com/123"))

    def test_ttl(self):
        thing = Thing(id="https://example.com/123")
        serialized: str = thing.serialize(format='ttl')
        print(serialized)
        g = rdflib.Graph()
        g.parse(data=serialized, format='ttl')
        res = g.query(_QUERY)
        bindings = res.bindings[0]
        self.assertEqual(bindings[rdflib.Variable("s")], rdflib.URIRef("https://example.com/123"))

    def test_n3(self):
        thing = Thing(id="https://example.com/123")
        serialized: str = thing.serialize(format='n3')
        print(serialized)
        g = rdflib.Graph()
        g.parse(data=serialized, format='n3')
        res = g.query(_QUERY)
        bindings = res.bindings[0]
        self.assertEqual(bindings[rdflib.Variable("s")], rdflib.URIRef("https://example.com/123"))
