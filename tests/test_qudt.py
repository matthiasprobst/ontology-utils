import unittest

import rdflib

from ontolutils.ex.qudt.utils import iri2str
from ontolutils.ex.qudt import Unit
from ontolutils.namespacelib import QUDT_UNIT
import pathlib
__this_dir__ = pathlib.Path(__file__).parent.resolve()
class TestQudt(unittest.TestCase):

    def test_iri2str(self):
        str1 = iri2str[str(QUDT_UNIT.M)]
        self.assertEqual(str1, "m")

    def test_unit(self):
        pascal_ttl = __this_dir__ / "data" / "qudt_unit_pa.ttl"
        # g = rdflib.Graph().parse(pascal_ttl)
        # ttl = g.serialize(format="ttl")
        u_pa = Unit.from_file(pascal_ttl, format="ttl", limit=1)
        print(u_pa.label)
        self.assertTrue("Pascal" in [str(l) for l in u_pa.label])
        print(u_pa.serialize(format="ttl"))
