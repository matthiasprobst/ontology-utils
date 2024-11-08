import logging
import unittest

import rdflib

import ontolutils
from ontolutils import namespacelib, set_logging_level
from ontolutils.namespacelib import _iana_utils

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

    def test_namespace_class_structure(self):
        from ontolutils import SCHEMA, M4I, CODEMETA, QUDT_UNIT, QUDT_KIND, OBO
        for ns in [SCHEMA, M4I, CODEMETA, QUDT_UNIT, QUDT_KIND, OBO]:
            self.assertIsInstance(ns, rdflib.namespace.DefinedNamespaceMeta)
            self.assertTrue(str(ns._NS).startswith('http'))
            self.assertIsInstance(ns.__annotations__, dict)
            self.assertTrue(len(ns.__annotations__) > 0, msg=f'No annotations found for {ns}')
            for k, v in ns.__annotations__.items():
                self.assertIsInstance(k, str)
                if k[0] != '_':
                    self.assertIsInstance(getattr(ns, k), rdflib.URIRef)

    def test_iana(self):
        self.assertEqual(namespacelib.IANA.application['zip'],
                         'https://www.iana.org/assignments/media-types/application/zip')

        self.assertEqual(namespacelib.IANA.audio['mp4'],
                         'https://www.iana.org/assignments/media-types/audio/mp4')
        self.assertEqual(namespacelib.IANA.image['png'],
                         'https://www.iana.org/assignments/media-types/image/png')

        self.assertEqual(namespacelib.IANA.text['html'],
                         'https://www.iana.org/assignments/media-types/text/html')

        self.assertEqual(namespacelib.IANA.video['mp4'],
                         'https://www.iana.org/assignments/media-types/video/mp4')

        self.assertEqual(namespacelib.IANA.model['gltf+json'],
                         'https://www.iana.org/assignments/media-types/model/gltf+json')

        self.assertEqual(namespacelib.IANA.multipart['form-data'],
                         'https://www.iana.org/assignments/media-types/multipart/form-data')

        self.assertEqual(namespacelib.IANA.application['json'],
                         'https://www.iana.org/assignments/media-types/application/json')

        self.assertEqual(namespacelib.IANA.application['ld+json'],
                         'https://www.iana.org/assignments/media-types/application/ld+json')

        self.assertEqual(namespacelib.IANA.message['http'],
                         'https://www.iana.org/assignments/media-types/message/http')

        self.assertEqual(namespacelib.IANA.font['woff'],
                         'https://www.iana.org/assignments/media-types/font/woff')

        # test download
        self.assertTrue(_iana_utils.iana_cache.is_dir())
        self.assertTrue(_iana_utils.iana_cache.exists())
        application_csv = _iana_utils.iana_cache / 'application.csv'
        application_csv.unlink(missing_ok=True)
        self.assertFalse(application_csv.exists())
        namespacelib._iana_utils.get_media_type('application')
        self.assertTrue(application_csv.exists())

    def test_m4i(self):
        self.assertIsInstance(ontolutils.M4I.Tool, rdflib.URIRef)
        self.assertIsInstance(namespacelib.M4I.Tool, rdflib.URIRef)
        self.assertEqual(str(namespacelib.M4I.Tool),
                         'https://w3id.org/nfdi4ing/metadata4ing#Tool')

        with self.assertRaises(AttributeError):
            namespacelib.M4I.Invalid

    def test_qudt_unit(self):
        self.assertIsInstance(namespacelib.QUDT_UNIT.M_PER_SEC, rdflib.URIRef)
        self.assertEqual(str(namespacelib.QUDT_UNIT.M_PER_SEC),
                         'https://qudt.org/vocab/unit/M-PER-SEC')
        with self.assertRaises(AttributeError):
            namespacelib.QUDT_UNIT.METER

    def test_qudt_kind(self):
        self.assertIsInstance(namespacelib.QUDT_KIND.Mass, rdflib.URIRef)
        self.assertEqual(str(namespacelib.QUDT_KIND.Mass),
                         'https://qudt.org/vocab/quantitykind/Mass')

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

    def test_hdf5(self):
        self.assertIsInstance(namespacelib.HDF5.File, rdflib.URIRef)
        self.assertEqual(str(namespacelib.HDF5.File),
                         "https://purl.allotrope.org/ontologies/hdf5/1.8#File")
