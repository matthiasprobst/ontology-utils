import pathlib
import unittest

__this_dir__ = pathlib.Path(__file__).parent

from ontolutils.ex import skos


class TestSkos(unittest.TestCase):

    def test_concept(self):
        concept = skos.Concept(
            id="http://example.org/concept/1",
            prefLabel="Example Concept@en",
        )
        self.assertEqual(
            concept.serialize("ttl"),
            """@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

<http://example.org/concept/1> a skos:Concept ;
    skos:prefLabel "Example Concept"@en .

"""
        )

    def test_ConceptScheme(self):
        concept = skos.Concept(
            id="http://example.org/concept/1",
            prefLabel="Example Concept@en",
        )
        scheme = skos.ConceptScheme(
            id="http://example.org/scheme/1",
            prefLabel="Example Scheme@en",
            has_top_concept=[concept],
        )
        self.assertEqual(scheme.serialize("ttl"),
                         """@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

<http://example.org/scheme/1> a skos:ConceptScheme ;
    skos:hasTopConcept <http://example.org/concept/1> .

<http://example.org/concept/1> a skos:Concept ;
    skos:prefLabel "Example Concept"@en .

""")
