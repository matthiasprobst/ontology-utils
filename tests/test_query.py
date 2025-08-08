import logging
import pathlib
import unittest

from pydantic import EmailStr

import ontolutils
from ontolutils import __version__
from ontolutils import set_logging_level

__this_dir__ = pathlib.Path(__file__).parent

LOG_LEVEL = logging.DEBUG


class TestQuery(unittest.TestCase):

    def setUp(self):
        logger = logging.getLogger('ontolutils')
        self.INITIAL_LOG_LEVEL = logger.level

        set_logging_level(LOG_LEVEL)

        assert logger.level == LOG_LEVEL

        @ontolutils.namespaces(prov="https://www.w3.org/ns/prov#",
                               foaf="http://xmlns.com/foaf/0.1/")
        @ontolutils.urirefs(Agent='prov:Agent',
                            mbox='foaf:mbox')
        class Agent(ontolutils.Thing):
            """Pydantic Model for https://www.w3.org/ns/prov#Agent"""
            mbox: EmailStr = None  # foaf:mbox

        self.Agent = Agent

    def test_dquery(self):
        test_data = """{"@context": {"foaf": "http://xmlns.com/foaf/0.1/", "prov": "http://www.w3.org/ns/prov#",
"schema": "http://www.w3.org/2000/01/rdf-schema#", "schema": "http://schema.org/",
"local": "http://example.org/"},
"@id": "local:testperson",
"@type": "prov:Person",
"foaf:firstName": "John",
"foaf:lastName": "Doe",
"age": 1,
"schema:affiliation": {
    "@id": "local:affiliation",
    "@type": "schema:Affiliation",
    "rdfs:label": "MyAffiliation"
    }
}"""
        res = ontolutils.dquery(
            subject="prov:Person", data=test_data,
            context={"prov": "http://www.w3.org/ns/prov#",
                     "local": "http://example.org",
                     "schema": "http://schema.org/"}
        )
        self.assertIsInstance(res, list)
        self.assertTrue(len(res) == 1)
        self.assertTrue(res[0]['@type'] == 'http://www.w3.org/ns/prov#Person')
        self.assertTrue(res[0]['@id'] == 'http://example.org/testperson')

    def test_dquery_codemeta(self):
        """Read the codemeta.json file and query for schema:SoftwareSourceCode"""
        codemeta_filename = __this_dir__ / '../codemeta.json'
        self.assertTrue(codemeta_filename.exists())
        res = ontolutils.dquery(
            subject="schema:SoftwareSourceCode",
            source=codemeta_filename,
            context={"schema": "http://schema.org/"}
        )
        self.assertIsInstance(res, list)
        self.assertTrue(len(res) == 1)
        self.assertTrue(res[0]['version'] == __version__)
        self.assertTrue('author' in res[0])
        print(res[0]['author'])
        self.assertIsInstance(res[0]['author'], list)
        self.assertEqual(res[0]['author'][0]['@type'], 'http://schema.org/Person')
        self.assertEqual(res[0]['author'][0]['givenName'], 'Matthias')

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
            subject='prov:Agent', source=__this_dir__ / 'agent1.jsonld',
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
        @ontolutils.urirefs(Student='prov:Student',
                            mbox='foaf:mbox',
                            age='foaf:age')
        class Student(ontolutils.Thing):
            """Pydantic Model for https://www.w3.org/ns/prov#Agent"""
            mbox: EmailStr = None  # foaf:mbox
            age: int = None

        @ontolutils.namespaces(prov="https://www.w3.org/ns/prov#",
                               foaf="http://xmlns.com/foaf/0.1/")
        @ontolutils.urirefs(SectionLeader='prov:SectionLeader',
                            hasStudent='foaf:hasStudent')
        class SectionLeader(ontolutils.Thing):
            """Pydantic Model for https://www.w3.org/ns/prov#Agent"""
            hasStudent: Student = None  # foaf:mbox

        @ontolutils.namespaces(prov="https://www.w3.org/ns/prov#",
                               foaf="http://xmlns.com/foaf/0.1/")
        @ontolutils.urirefs(Professor='prov:Professor',
                            hasSectionLeader='foaf:hasSectionLeader')
        class Professor(ontolutils.Thing):
            """Pydantic Model for https://www.w3.org/ns/prov#Agent"""
            hasSectionLeader: SectionLeader = None  # foaf:mbox

        section_leader = SectionLeader(label='section_leader',
                                       hasStudent=Student(label='student', age=30))
        prof = Professor(label='Professor',
                         hasSectionLeader=section_leader)

        with open(__this_dir__ / 'supersuperagent.json', 'w') as f:
            f.write(prof.model_dump_jsonld())

        p = Professor.from_jsonld(__this_dir__ / 'supersuperagent.json')[0]
        self.assertEqual(p.label, 'Professor')
        self.assertEqual(p.hasSectionLeader.label, 'section_leader')
        self.assertEqual(p.hasSectionLeader.hasStudent.label, 'student')
        self.assertEqual(p.hasSectionLeader.hasStudent.age, 30)

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

        with open(__this_dir__ / 'agent.jsonld', 'w') as f:
            f.write(
                """
                {
                    "@context": {
                        "prov": "https://www.w3.org/ns/prov#",
                        "foaf": "http://xmlns.com/foaf/0.1/",
                        "local": "http:/local.org/"
                    },
                    "@graph": [
                        {
                            "@id": "local:agent1",
                            "@type": "prov:Agent",
                            "foaf:mbox": "a@mail.com"
                        },
                        {
                            "@id": "local:agent2",
                            "@type": "prov:Agent",
                            "foaf:mbox": "b@mail.com"
                        },
                        {
                            "@id": "local:agent3",
                            "@type": "prov:Agent",
                            "foaf:mbox": "c@mail.com"
                        }
                    ]
                }"""
            )
        found_agents = ontolutils.query(
            self.Agent, source=__this_dir__ / 'agent.jsonld',
            limit=2)
        self.assertEqual(len(found_agents), 2)
        self.assertEqual(found_agents[0].mbox, 'a@mail.com')
        self.assertEqual(found_agents[1].mbox, 'b@mail.com')

        # find none:

        @ontolutils.namespaces(prov="https://www.w3.org/ns/prov#",
                               foaf="http://xmlns.com/foaf/0.1/")
        @ontolutils.urirefs(Mything='prov:Mything')
        class Mything(ontolutils.Thing):
            pass

        found_Mything = ontolutils.query(Mything, source=__this_dir__ / 'agent.jsonld')
        self.assertEqual(len(found_Mything), 0)

        found_Mything = ontolutils.dquery(subject="prov:Mything",
                                          source=__this_dir__ / 'agent.jsonld',
                                          context=None
                                          )
        self.assertEqual(len(found_Mything), 0)

    def tearDown(self):
        pathlib.Path(__this_dir__ / 'agent.jsonld').unlink(missing_ok=True)
        pathlib.Path(__this_dir__ / 'agents.jsonld').unlink(missing_ok=True)
        pathlib.Path(__this_dir__ / 'superagent.json').unlink(missing_ok=True)
        pathlib.Path(__this_dir__ / 'supersuperagent.json').unlink(missing_ok=True)

        set_logging_level(self.INITIAL_LOG_LEVEL)
        assert logging.getLogger('ontolutils').level == self.INITIAL_LOG_LEVEL
