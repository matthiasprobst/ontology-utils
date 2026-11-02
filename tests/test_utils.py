import unittest

import rdflib
from pydantic import EmailStr

import ontolutils
from ontolutils import Thing
from ontolutils import namespaces, urirefs
from ontolutils import set_logging_level
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
        ns, name = utils.split_uri('http://xmlns.com/foaf/0.1/Agent')
        self.assertEqual(ns, 'http://xmlns.com/foaf/0.1/')
        self.assertEqual(name, 'Agent')

    def test_parse_qudt_units(self):
        self.assertEqual(ontolutils.parse_unit('m/s'), rdflib.URIRef('http://qudt.org/vocab/unit/M-PER-SEC'))
