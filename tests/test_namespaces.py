import logging
import unittest

import rdflib

import ontolutils
from ontolutils import namespacelib, set_logging_level

LOG_LEVEL = logging.DEBUG


class TestNamespaces(unittest.TestCase):
    def setUp(self):
        logger = logging.getLogger('ontolutils')
        self.INITIAL_LOG_LEVEL = logger.level

        set_logging_level(LOG_LEVEL)

        assert logger.level == LOG_LEVEL

    def tearDown(self):
        set_logging_level(self.INITIAL_LOG_LEVEL)
        assert logging.getLogger('ontolutils').level == self.INITIAL_LOG_LEVEL

    def test_iana(self):
        self.assertEqual(namespacelib.IANA.application['zip'],
                         'https://www.iana.org/assignments/media-types/application/zip')

    def test_m4i(self):
        self.assertIsInstance(ontolutils.M4I.Tool, rdflib.URIRef)
        self.assertIsInstance(namespacelib.M4I.Tool, rdflib.URIRef)
        self.assertEqual(str(namespacelib.M4I.Tool),
                         'http://w3id.org/nfdi4ing/metadata4ing#Tool')

        with self.assertRaises(AttributeError):
            namespacelib.M4I.Invalid

    def test_qudt_unit(self):
        self.assertIsInstance(namespacelib.QUDT_UNIT.M_PER_SEC, rdflib.URIRef)
        self.assertEqual(str(namespacelib.QUDT_UNIT.M_PER_SEC),
                         'http://qudt.org/vocab/unit/M-PER-SEC')
        with self.assertRaises(AttributeError):
            namespacelib.QUDT_UNIT.METER

    def test_qudt_kind(self):
        self.assertIsInstance(namespacelib.QUDT_KIND.Mass, rdflib.URIRef)
        self.assertEqual(str(namespacelib.QUDT_KIND.Mass),
                         'http://qudt.org/vocab/quantitykind/Mass')

    def test_rdflib(self):
        self.assertIsInstance(rdflib.PROV.Agent, rdflib.URIRef)
        self.assertEqual(str(rdflib.PROV.Agent),
                         "http://www.w3.org/ns/prov#Agent")

    def test_codemeta(self):
        self.assertIsInstance(namespacelib.CODEMETA.softwareSuggestions, rdflib.URIRef)
        self.assertEqual(str(namespacelib.CODEMETA.softwareSuggestions),
                         "https://codemeta.github.io/terms/softwareSuggestions")

    def test_schema(self):
        self.assertIsInstance(namespacelib.SCHEMA.Person, rdflib.URIRef)
        self.assertEqual(str(namespacelib.SCHEMA.Person),
                         "https://schema.org/Person")

    def test_ssno(self):
        self.assertIsInstance(namespacelib.SSNO.StandardName, rdflib.URIRef)
        self.assertEqual(str(namespacelib.SSNO.StandardName),
                         "https://matthiasprobst.github.io/ssno#StandardName")
        with self.assertRaises(AttributeError):
            namespacelib.SSNO.METER
