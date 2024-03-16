import json
import logging
import unittest

import pydantic
from pydantic import EmailStr

from ontolutils import Thing
from ontolutils import set_logging_level
from ontolutils import urirefs, namespaces
from ontolutils.classes import decorator

LOG_LEVEL = logging.DEBUG


class TestNamespaces(unittest.TestCase):

    def setUp(self):
        logger = logging.getLogger('ontolutils')
        self.INITIAL_LOG_LEVEL = logger.level

        set_logging_level(LOG_LEVEL)

        assert logger.level == LOG_LEVEL

    def tearDown(self):
        set_logging_level(self.INITIAL_LOG_LEVEL)
        assert logging.getLogger('ontolutils').level == self.INITIAL_LOG_LEVEL

    def test_sort_classes(self):
        thing1 = Thing(label='Thing 1')
        thing2 = Thing(label='Thing 2')
        self.assertFalse(thing1 < thing2)
        with self.assertRaises(TypeError):
            thing1 < 4
        thing1 = Thing(label='Thing 1', id='http://example.com/thing1')
        thing2 = Thing(label='Thing 2', id='http://example.com/thing2')
        self.assertTrue(thing1 < thing2)

    def test__repr_html_(self):
        thing = Thing(label='Thing 1')
        self.assertEqual(thing._repr_html_(), 'Thing(label=Thing 1)')

    def test_thing_get_jsonld_dict(self):
        with self.assertRaises(pydantic.ValidationError):
            _ = Thing(id=1, label='Thing 1')

        thing = Thing(id='https://example.org/TestThing', label='Test Thing')
        with self.assertRaises(TypeError):
            thing.get_jsonld_dict(context=1)

        thing_dict = thing.get_jsonld_dict()
        self.assertIsInstance(thing_dict, dict)
        self.assertDictEqual(thing_dict['@context'], {'local': 'http://example.org/',
                                                      'owl': 'http://www.w3.org/2002/07/owl#',
                                                      'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'})
        self.assertEqual(thing_dict['@id'], 'https://example.org/TestThing')
        self.assertEqual(thing_dict['rdfs:label'], 'Test Thing')
        self.assertEqual(thing_dict['@type'], 'owl:Thing')

    def test_decorator(self):
        self.assertTrue(decorator._is_http_url('http://example.com/'))
        self.assertFalse(decorator._is_http_url('example.com/'))

    def test_model_dump_jsonld(self):
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

        agent = Agent(
            label='Agent 1',
            mbox='my@email.com'
        )
        with self.assertRaises(pydantic.ValidationError):
            agent.mbox = 4.5
            agent.model_validate(agent.model_dump())
        agent.mbox = 'my@email.com'
        jsonld_str1 = agent.model_dump_jsonld(rdflib_serialize=False)
        jsonld_str2 = agent.model_dump_jsonld(rdflib_serialize=True)
        jsonld_str2_dict = json.loads(jsonld_str2)
        self.assertNotEqual(
            json.loads(jsonld_str1),
            jsonld_str2_dict
        )

        agent1_dict = json.loads(jsonld_str1)
        agent1_dict.pop('@id')

        agent2_dict = jsonld_str2_dict
        agent2_dict.pop('@id')

        self.assertDictEqual(agent1_dict,
                             agent2_dict)

        # jsonld_str2_dict.pop('@id')
        # self.assertEqual(
        #     json.loads(jsonld_str1),
        #     jsonld_str2_dict
        # )

        # serialize with a "@import"
        jsonld_str3 = agent.model_dump_jsonld(
            rdflib_serialize=False,
            context={
                '@import': 'https://git.rwth-aachen.de/nfdi4ing/metadata4ing/metadata4ing/-/raw/master/m4i_context.jsonld'
            }
        )
        jsonld_str3_dict = json.loads(jsonld_str3)
        self.assertEqual(
            jsonld_str3_dict['@context']['@import'],
            'https://git.rwth-aachen.de/nfdi4ing/metadata4ing/metadata4ing/-/raw/master/m4i_context.jsonld'
        )

    def test_model_dump_jsonld_nested(self):
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

        @namespaces(schema="https://schema.org/")
        @urirefs(Organization='prov:Organization')
        class Organization(Agent):
            """Pydantic Model for https://www.w3.org/ns/prov/Agent"""

        @namespaces(schema="https://schema.org/")
        @urirefs(Person='foaf:Person',
                 affiliation='schema:affiliation')
        class Person(Agent):
            firstName: str = None
            affiliation: Organization = None

        person = Person(
            label='Person 1',
            affiliation=Organization(
                label='Organization 1'
            ),
        )
        jsonld_str = person.model_dump_jsonld()

    def test_prov(self):
        @namespaces(prov="https://www.w3.org/ns/prov#",
                    foaf="http://xmlns.com/foaf/0.1/")
        @urirefs(Agent='prov:Agent',
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
        self.assertEqual(agent.mbox, agent.model_dump()['mbox'])
        self.assertEqual(Agent.iri(), 'https://www.w3.org/ns/prov#Agent')
        self.assertEqual(Agent.iri(compact=True), 'prov:Agent')
        self.assertEqual(Agent.iri('mbox'), 'http://xmlns.com/foaf/0.1/mbox')
        self.assertEqual(Agent.iri('mbox', compact=True), 'foaf:mbox')
