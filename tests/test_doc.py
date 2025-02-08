import logging
import unittest

import rdflib

from ontolutils.namespacelib import QUDT_UNIT

LOG_LEVEL = logging.DEBUG


class TestDoc(unittest.TestCase):

    def test_doc1(self):
        self.assertEqual(
            rdflib.URIRef('http://qudt.org/vocab/unit/M-PER-SEC'),
            QUDT_UNIT.M_PER_SEC)
