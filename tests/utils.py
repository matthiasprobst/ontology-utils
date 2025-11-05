import unittest

import rdflib


class ClassTest(unittest.TestCase):
    test_jsonld_filename = 'https://raw.githubusercontent.com/matthiasprobst/ssnolib/main/tests/data/piv_dataset.jsonld'

    def setUp(self):
        self.maxDiff = None

    def check_jsonld_string(self, jsonld_string):
        g = rdflib.Graph()
        g.parse(data=jsonld_string, format='json-ld',
                context={'m4i': 'http://w3id.org/nfdi4ing/metadata4ing#',
                         'rdf': 'https://www.w3.org/1999/02/22-rdf-syntax-ns#',
                         'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'})
        self.assertTrue(len(g) > 0)
        for s, p, o in g:
            self.assertIsInstance(p, rdflib.URIRef)
