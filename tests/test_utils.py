import pathlib
import unittest

from pydantic import EmailStr

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

        self.assertEqual({}, unm.get(Agent))
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
        print(text_filename)
        self.assertTrue(text_filename.parent.parent == get_cache_dir())
