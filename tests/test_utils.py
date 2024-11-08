import pathlib
import shutil
import unittest
from hashlib import sha256

import rdflib
from pydantic import EmailStr

import ontolutils
from ontolutils import Thing
from ontolutils import namespaces, urirefs
from ontolutils import set_logging_level
from ontolutils.cache import get_cache_dir
from ontolutils.classes import utils

set_logging_level('WARNING')


class TestUtils(unittest.TestCase):

    def test_UNManager(self):
        unm = utils.UNManager()
        self.assertEqual(unm.__repr__(), 'UNManager()')

        @namespaces(foaf="http://xmlns.com/foaf/0.1/")
        @urirefs(Agent='foaf:Agent',
                 mbox='foaf:mbox')
        class Agent(Thing):
            """Pydantic Model for http://xmlns.com/foaf/0.1/Agent
            Parameters
            ----------
            mbox: EmailStr = None
                Email address (foaf:mbox)
            """
            mbox: EmailStr = None

        self.assertEqual({}, unm.get(Agent, {}))
        self.assertEqual(None, unm.get(Agent, None))
        unm[Agent]['foaf'] = 'http://xmlns.com/foaf/0.1/'
        self.assertEqual(unm.__repr__(), f'UNManager({Agent.__name__})')

    def test_split_uriref(self):
        ns, name = utils.split_URIRef('foaf:Agent')
        self.assertEqual(ns, 'foaf')
        self.assertEqual(name, 'Agent')

        ns, name = utils.split_URIRef('http://xmlns.com/foaf/0.1/Agent')
        self.assertEqual(ns, 'http://xmlns.com/foaf/0.1/')
        self.assertEqual(name, 'Agent')

        ns, name = utils.split_URIRef('Agent')
        self.assertEqual(ns, None)
        self.assertEqual(name, 'Agent')

    def test_download(self):
        text_filename = utils.download_file('https://www.iana.org/assignments/media-types/text.csv')

        self.assertIsInstance(text_filename, pathlib.Path)
        self.assertTrue(text_filename.exists())
        self.assertTrue(text_filename.parent.parent == get_cache_dir())

        # compute hash:
        with open(text_filename, 'rb') as f:
            hash = sha256(f.read()).hexdigest()
        text_filename = utils.download_file('https://www.iana.org/assignments/media-types/text.csv',
                                            known_hash=hash,
                                            dest_filename='not/existing/dir')
        self.assertTrue(text_filename.parent, 'dir')

        text_filename = utils.download_file('https://www.iana.org/assignments/media-types/text.csv',
                                            known_hash=hash,
                                            dest_filename='not/existing/dir',
                                            overwrite_existing=False)
        self.assertTrue(text_filename.exists())

        text_filename = utils.download_file('https://www.iana.org/assignments/media-types/text.csv',
                                            known_hash=hash,
                                            dest_filename='not/existing/dir',
                                            overwrite_existing=True)
        self.assertTrue(text_filename.exists())

        text_filename.unlink(missing_ok=True)

        if pathlib.Path('not/existing/dir').exists():
            shutil.rmtree('not/existing/dir')

    def test_parse_qudt_units(self):
        self.assertEqual(ontolutils.parse_unit('m/s'), rdflib.URIRef('https://qudt.org/vocab/unit/M-PER-SEC'))