import unittest

from ontolutils.ex.qudt.utils import iri2str
from ontolutils.namespacelib import QUDT_UNIT


class TestQudt(unittest.TestCase):

    def test_iri2str(self):
        str1 = iri2str[str(QUDT_UNIT.M)]
        self.assertEqual(str1, "m")
