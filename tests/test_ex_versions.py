import unittest


class TestExVersions(unittest.TestCase):

    def test_dcat(self):
        from ontolutils.ex.dcat import __version__
        self.assertEqual("3.0", __version__)

    def test_foaf(self):
        from ontolutils.ex.foaf import __version__
        self.assertEqual("0.1", __version__)

    def test_hdf5(self):
        from ontolutils.ex.hdf5 import __version__
        self.assertEqual("REC/2024/12", __version__)

    def test_m4i(self):
        from ontolutils.ex.m4i import __version__
        self.assertEqual("1.4.0", __version__)

    def test_pimsii(self):
        from ontolutils.ex.pimsii import __version__
        self.assertEqual("II.1.12a", __version__)

    def test_prov(self):
        from ontolutils.ex.prov import __version__
        self.assertEqual("2013.19.05", __version__)

    def test_qudt(self):
        from ontolutils.ex.qudt import __version__
        self.assertEqual("3.1.9", __version__)

    def test_schema(self):
        from ontolutils.ex.schema import __version__
        self.assertEqual("29.4", __version__)

    def test_sis(self):
        from ontolutils.ex.sis import __version__
        self.assertEqual("0.2.1", __version__)

    def test_skos(self):
        from ontolutils.ex.skos import __version__
        self.assertEqual("2004/02", __version__)

    def test_spdx(self):
        from ontolutils.ex.spdx import __version__
        self.assertEqual("2.3", __version__)

    def test_ssn(self):
        from ontolutils.ex.ssn import __version__
        self.assertEqual("2017.10.19", __version__)
