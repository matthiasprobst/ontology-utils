import pathlib
import unittest

from pydantic import EmailStr

import ontolutils

__this_dir__ = pathlib.Path(__file__).parent


class TestQuery(unittest.TestCase):

    def setUp(self):
        @ontolutils.namespaces(prov="https://www.w3.org/ns/prov#",
                               foaf="http://xmlns.com/foaf/0.1/")
        @ontolutils.urirefs(Agent='prov:Agent',
                            mbox='foaf:mbox')
        class Agent(ontolutils.Thing):
            """Pydantic Model for https://www.w3.org/ns/prov#Agent"""
            mbox: EmailStr = None  # foaf:mbox

        self.Agent = Agent

    def test_query(self):
        agent = self.Agent(mbox='e@mail.com')
        with open(__this_dir__ / 'agent.jsonld', 'w') as f:
            json_ld_str = agent.model_dump_jsonld(context={'prov': 'https://www.w3.org/ns/prov#',
                                                     'foaf': 'http://xmlns.com/foaf/0.1/'})
            f.write(
                json_ld_str
            )
        found_agents = ontolutils.query(self.Agent, source=__this_dir__ / 'agent.jsonld')
        self.assertEqual(len(found_agents), 1)
        self.assertEqual(found_agents[0].mbox, 'e@mail.com')

        found_agents = sorted(ontolutils.query(self.Agent, source=__this_dir__ / 'agents.jsonld'))
        self.assertEqual(len(found_agents), 2)
        self.assertEqual(found_agents[0].mbox, 'e1@mail.com')
        self.assertEqual(found_agents[1].mbox, 'e2@mail.com')

    def tearDown(self):
        pathlib.Path(__this_dir__ / 'agent.jsonld').unlink(missing_ok=True)
