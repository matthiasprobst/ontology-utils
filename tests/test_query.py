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

    def test_query_get_dict(self):
        """query excepts a class or a type string"""
        agent1 = self.Agent(
            label='agent1',
        )
        agent2 = self.Agent(
            label='agent2',
        )

        agents_jsonld = ontolutils.merge_jsonld(
            [agent1.model_dump_jsonld(),
             agent2.model_dump_jsonld()]
        )

        with open(__this_dir__ / 'agent1.jsonld', 'w') as f:
            f.write(
                agents_jsonld
            )
        agents = ontolutils.dquery(
            type='prov:Agent', source=__this_dir__ / 'agent1.jsonld',
            context={'prov': 'https://www.w3.org/ns/prov#',
                     'foaf': 'http://xmlns.com/foaf/0.1/'}
        )
        self.assertEqual(len(agents), 2)
        self.assertEqual(agents[0]['label'], 'agent1')
        self.assertEqual(agents[1]['label'], 'agent2')

        agent_load = self.Agent.from_jsonld(__this_dir__ / 'agent1.jsonld', limit=1)
        self.assertEqual(agent_load.label, 'agent1')

        (__this_dir__ / 'agent1.jsonld').unlink(missing_ok=True)

    def test_query_multiple_classes_in_jsonld(self):
        from ontolutils.classes.utils import merge_jsonld

        agent1 = self.Agent(
            label='agent1',
        )
        agent2 = self.Agent(
            label='agent2',
        )
        merged_jsonld = merge_jsonld([agent1.model_dump_jsonld(),
                                      agent2.model_dump_jsonld()])
        with open(__this_dir__ / 'agents.jsonld', 'w') as f:
            f.write(merged_jsonld)

        agentX = self.Agent.from_jsonld(__this_dir__ / 'agents.jsonld')
        self.assertEqual(len(agentX), 2)
        self.assertEqual(agentX[0].label, 'agent1')
        self.assertEqual(agentX[1].label, 'agent2')

    def test_recursive_query(self):
        @ontolutils.namespaces(prov="https://www.w3.org/ns/prov#",
                               foaf="http://xmlns.com/foaf/0.1/")
        @ontolutils.urirefs(Agent='prov:Agent',
                            mbox='foaf:mbox')
        class Agent(ontolutils.Thing):
            """Pydantic Model for https://www.w3.org/ns/prov#Agent"""
            mbox: EmailStr = None  # foaf:mbox

        @ontolutils.namespaces(prov="https://www.w3.org/ns/prov#",
                               foaf="http://xmlns.com/foaf/0.1/")
        @ontolutils.urirefs(SuperAgent='prov:SuperAgent',
                            hasAgent='foaf:hasAgent')
        class SuperAgent(ontolutils.Thing):
            """Pydantic Model for https://www.w3.org/ns/prov#Agent"""
            hasAgent: Agent = None  # foaf:mbox

        @ontolutils.namespaces(prov="https://www.w3.org/ns/prov#",
                               foaf="http://xmlns.com/foaf/0.1/")
        @ontolutils.urirefs(SuperSuperAgent='prov:SuperSuperAgent',
                            hasSuperAgent='foaf:hasSuperAgent')
        class SuperSuperAgent(ontolutils.Thing):
            """Pydantic Model for https://www.w3.org/ns/prov#Agent"""
            hasSuperAgent: SuperAgent = None  # foaf:mbox

        superagent = SuperAgent(label='superagent',
                                hasAgent=Agent(label='agent1'))
        supersuperagent = SuperSuperAgent(label='supersuperagent',
                                          hasSuperAgent=superagent)

        with open(__this_dir__ / 'supersuperagent.json', 'w') as f:
            f.write(supersuperagent.model_dump_jsonld())

        cc = SuperSuperAgent.from_jsonld(__this_dir__ / 'supersuperagent.json')[0]
        self.assertEqual(cc.hasSuperAgent.hasAgent.label, 'agent1')
        self.assertEqual(cc.hasSuperAgent.label, 'superagent')
        self.assertEqual(cc.label, 'supersuperagent')

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

    def tearDown(self):
        pathlib.Path(__this_dir__ / 'agent.jsonld').unlink(missing_ok=True)
        pathlib.Path(__this_dir__ / 'agents.jsonld').unlink(missing_ok=True)
        pathlib.Path(__this_dir__ / 'superagent.json').unlink(missing_ok=True)
        pathlib.Path(__this_dir__ / 'supersuperagent.json').unlink(missing_ok=True)
