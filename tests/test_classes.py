import unittest

import pydantic
from pydantic import EmailStr

from ontolutils import Thing
from ontolutils import classes as ontocls


class TestNamespaces(unittest.TestCase):

    def test_prov(self):
        @ontocls.namespaces(prov="https://www.w3.org/ns/prov#",
                            foaf="http://xmlns.com/foaf/0.1/")
        @ontocls.urirefs(Agent='prov:Agent',
                         mbox='foaf:mbox')
        class Agent(Thing):
            """Pydantic Model for https://www.w3.org/ns/prov#Agent
            Parameters
            ----------
            mbox: EmailStr = None
                Email address (foaf:mbox)
            """
            mbox: EmailStr = None  # foaf:mbox

        with self.assertRaises(pydantic.ValidationError):
            agent = Agent(mbox='123')

        agent = Agent(mbox='m@email.com')
        self.assertEqual(agent.mbox, 'm@email.com')
        self.assertEqual(agent.mbox, agent.dict()['mbox'])
        self.assertEqual(Agent.iri(), 'https://www.w3.org/ns/prov#Agent')
        self.assertEqual(Agent.iri(compact=True), 'prov:Agent')
        self.assertEqual(Agent.iri('mbox'), 'http://xmlns.com/foaf/0.1/mbox')
        self.assertEqual(Agent.iri('mbox', compact=True), 'foaf:mbox')
