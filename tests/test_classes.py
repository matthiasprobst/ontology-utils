import datetime
import json
import logging
import unittest

import pydantic
import rdflib
from pydantic import EmailStr

from ontolutils import Thing, urirefs, namespaces, get_urirefs, get_namespaces
from ontolutils import set_logging_level
from ontolutils.classes import decorator
from ontolutils.classes.thing import resolve_iri
from ontolutils.classes.utils import split_URIRef

LOG_LEVEL = logging.DEBUG


class TestNamespaces(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        logger = logging.getLogger('ontolutils')
        self.INITIAL_LOG_LEVEL = logger.level

        set_logging_level(LOG_LEVEL)

        assert logger.level == LOG_LEVEL

    def tearDown(self):
        set_logging_level(self.INITIAL_LOG_LEVEL)
        assert logging.getLogger('ontolutils').level == self.INITIAL_LOG_LEVEL

    def test_resolve_iri(self):
        ret = resolve_iri('foaf:age', context={'foaf': 'http://xmlns.com/foaf/0.1/'})
        self.assertEqual(ret, 'http://xmlns.com/foaf/0.1/age')
        ret = resolve_iri('age', context={'foaf': 'http://xmlns.com/foaf/0.1/'})
        self.assertEqual(ret, None)
        ret = resolve_iri('age', context={'age': 'http://xmlns.com/foaf/0.1/age'})
        self.assertEqual(ret, 'http://xmlns.com/foaf/0.1/age')
        ret = resolve_iri('label', context={'age': 'http://xmlns.com/foaf/0.1/age'})
        self.assertEqual(ret, 'http://www.w3.org/2000/01/rdf-schema#label')
        ret = resolve_iri('label', context={'label': {'@id': 'http://www.w3.org/2000/01/rdf-schema#label'}})
        self.assertEqual(ret, 'http://www.w3.org/2000/01/rdf-schema#label')
        ret = resolve_iri('prefix:label', {})
        self.assertEqual(ret, None)

    def test_split_URIRef(self):
        self.assertListEqual(split_URIRef(rdflib.URIRef('http://example.com/')),
                             ['http://example.com/', ''])
        self.assertListEqual(split_URIRef(rdflib.URIRef('http://example.com/#test')),
                             ['http://example.com/#', 'test'])
        self.assertListEqual(split_URIRef(rdflib.URIRef('http://example.com/test')),
                             ['http://example.com/', 'test'])
        self.assertListEqual(split_URIRef(rdflib.URIRef('http://example.com/test#test')),
                             ['http://example.com/test#', 'test'])
        self.assertListEqual(split_URIRef(rdflib.URIRef('http://example.com/test:123')),
                             ['http://example.com/', 'test:123'])

    def test_thing_custom_prop(self):
        """It is helpful to have the properties equal to the urirefs keys,
        however, this should not be required!"""

        @namespaces(foaf='http://xmlns.com/foaf/0.1/',
                    prov='http://www.w3.org/ns/prov#')
        @urirefs(Person='prov:Person',
                 first_name='foaf:firstName',
                 lastName='foaf:lastName',
                 age='foaf:age')
        class Person(Thing):
            first_name: str = None
            lastName: str
            age: int = None

        p = Person(first_name='John', lastName='Doe', age=23)
        print(p.model_dump_jsonld(resolve_keys=True))
        p_from_jsonld = Person.from_jsonld(data=p.model_dump_jsonld(resolve_keys=True), limit=1)
        self.assertEqual(p_from_jsonld.first_name, 'John')
        self.assertEqual(p_from_jsonld.lastName, 'Doe')
        self.assertEqual(p_from_jsonld.age, 23)

        p_from_jsonld = Person.from_jsonld(data=p.model_dump_jsonld(resolve_keys=False), limit=1)
        self.assertEqual(p_from_jsonld.first_name, 'John')
        self.assertEqual(p_from_jsonld.lastName, 'Doe')
        self.assertEqual(p_from_jsonld.age, 23)

        p_from_jsonld = Person.from_jsonld(data=p.model_dump_jsonld(resolve_keys=True), limit=None)
        self.assertEqual(p_from_jsonld[0].first_name, 'John')
        self.assertEqual(p_from_jsonld[0].lastName, 'Doe')
        self.assertEqual(p_from_jsonld[0].age, 23)

        p_from_jsonld = Person.from_jsonld(data=p.model_dump_jsonld(resolve_keys=False), limit=None)
        self.assertEqual(p_from_jsonld[0].first_name, 'John')
        self.assertEqual(p_from_jsonld[0].lastName, 'Doe')
        self.assertEqual(p_from_jsonld[0].age, 23)

        # add additional non-urirefs property:
        p.height = 183
        self.assertEqual(p.height, 183)
        self.assertEqual(json.loads(p.model_dump_jsonld(resolve_keys=True))['height'], 183)
        p183_from_jsonld = Person.from_jsonld(data=p.model_dump_jsonld(resolve_keys=True), limit=1)
        with self.assertRaises(AttributeError):  # height is not defined!
            p183_from_jsonld.height

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

        thing = Thing(id='https://example.org/TestThing', label='Test Thing', numerical_value=1.0,
                      dt=datetime.datetime(2021, 1, 1))
        with self.assertRaises(TypeError):
            thing.get_jsonld_dict(context=1)

        thing_dict = thing.get_jsonld_dict()
        self.assertIsInstance(thing_dict, dict)
        self.assertDictEqual(thing_dict['@context'],
                             {'owl': 'http://www.w3.org/2002/07/owl#',
                              'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'})
        self.assertEqual(thing_dict['@id'], 'https://example.org/TestThing')
        self.assertEqual(thing_dict['rdfs:label'], 'Test Thing')
        self.assertEqual(thing_dict['@type'], 'owl:Thing')

    def test_decorator(self):
        self.assertTrue(decorator._is_http_url('http://example.com/'))
        self.assertFalse(decorator._is_http_url('example.com/'))
        self.assertFalse(decorator._is_http_url('http:invalid.123'))

    def test_model_dump_jsonld(self):
        @namespaces(foaf="http://xmlns.com/foaf/0.1/")
        @urirefs(Agent='foaf:Agent',
                 mbox='foaf:mbox',
                 age='foaf:age')
        class Agent(Thing):
            """Pydantic Model for http://xmlns.com/foaf/0.1/Agent
            Parameters
            ----------
            mbox: EmailStr = None
                Email address (foaf:mbox)
            """
            mbox: EmailStr = None
            age: int = None

        agent = Agent(
            label='Agent 1',
            mbox='my@email.com',
            age=23,
        )

        with self.assertRaises(pydantic.ValidationError):
            agent.mbox = 4.5
            agent.model_validate(agent.model_dump())
        agent.mbox = 'my@email.com'
        jsonld_str1 = agent.model_dump_jsonld(rdflib_serialize=False)

        self.assertIsInstance(json.loads(jsonld_str1)['foaf:age'], int)

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

    def test_model_dump_jsonld_and_load_with_import(self):
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
        ns = agent.namespaces
        jsonld_string = agent.model_dump_jsonld(
            context={
                "@import": 'https://raw.githubusercontent.com/matthiasprobst/pivmeta/main/pivmeta_context.jsonld'
            }
        )
        self.assertDictEqual(agent.namespaces, ns)
        self.assertTrue('@import' in json.loads(jsonld_string)['@context'])
        loaded_agent = Agent.from_jsonld(data=jsonld_string, limit=1)
        self.assertDictEqual(loaded_agent.namespaces, ns)
        self.assertEqual(loaded_agent.mbox, agent.mbox)

    def test_schema_http(self):
        @namespaces(foaf="http://xmlns.com/foaf/0.1/",
                    schema="https://schema.org/")
        @urirefs(Agent='foaf:Agent',
                 name='schema:name')
        class Agent(Thing):
            name: str

        agent = Agent(name='John Doe')
        self.assertEqual(agent.name, 'John Doe')
        agent_jsonld = agent.model_dump_jsonld()
        print(agent_jsonld.replace('https://schema', 'http://schema'))
        with self.assertWarns(UserWarning):
            agent.from_jsonld(data=agent_jsonld.replace('https://schema', 'http://schema'),
                              limit=1)

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

        @namespaces(schema="http://schema.org/")
        @urirefs(Organization='prov:Organization')
        class Organization(Agent):
            """Pydantic Model for https://www.w3.org/ns/prov/Agent"""

        @namespaces(schema="http://schema.org/")
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

    def test_person(self):
        @namespaces(prov="http://www.w3.org/ns/prov#",
                    foaf="http://xmlns.com/foaf/0.1/")
        @urirefs(Person='prov:Person',
                 firstName='foaf:firstName',
                 # lastName=FOAF.lastName,
                 lastName='foaf:lastName',
                 mbox='foaf:mbox')
        class Person(Thing):
            firstName: str
            lastName: str = None
            mbox: EmailStr = None

        p = Person(id="local:cde4c79c-21f2-4ab7-b01d-28de6e4aade4", firstName='John', lastName='Doe')
        jsonld = {
            "@context": {
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "foaf": "http://xmlns.com/foaf/0.1/",
                "prov": "http://www.w3.org/ns/prov#",
            },
            "@id": "local:cde4c79c-21f2-4ab7-b01d-28de6e4aade4",
            "@type": "prov:Person",
            "foaf:firstName": "John",
            "foaf:lastName": "Doe"
        }
        print(p.model_dump_jsonld())

        self.assertDictEqual(json.loads(p.model_dump_jsonld()),
                             jsonld)

    def test_update_namespace_and_uri(self):
        class CustomPerson(Thing):
            pass

        mt = CustomPerson()
        # custom person has no
        self.assertDictEqual(mt.urirefs, get_urirefs(Thing))
        self.assertDictEqual(mt.urirefs, {'Thing': 'owl:Thing', 'label': 'rdfs:label'})
        self.assertDictEqual(mt.namespaces, get_namespaces(Thing))
        self.assertDictEqual(mt.namespaces, {'owl': 'http://www.w3.org/2002/07/owl#',
                                             'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'})

        mt = CustomPerson(first_name='John', last_name='Doe')
        with self.assertRaises(AttributeError):
            mt.namespaces = 'http://xmlns.com/foaf/0.1/'
        with self.assertRaises(AttributeError):
            mt.urirefs = 'foaf:lastName'

        mt.namespaces['foaf'] = 'http://xmlns.com/foaf/0.1/'
        mt.urirefs['first_name'] = 'foaf:firstName'
        mt.urirefs['last_name'] = 'foaf:lastName'
        # print(mt.model_dump_json(indent=2, exclude_none=True))
        ref_jsonld = {
            "@context": {
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "foaf": "http://xmlns.com/foaf/0.1/"
            },
            "@type": "CustomPerson",
            "foaf:firstName": "John",
            "foaf:lastName": "Doe"
        }
        jsonld_dict = json.loads(mt.model_dump_jsonld(resolve_keys=True))
        jsonld_dict.pop('@id')
        self.assertDictEqual(jsonld_dict,
                             ref_jsonld)

        ref_jsonld = {
            "@context": {
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "foaf": "http://xmlns.com/foaf/0.1/",
                "first_name": "http://xmlns.com/foaf/0.1/firstName",
                "last_name": "http://xmlns.com/foaf/0.1/lastName"
            },
            "@type": "CustomPerson",
            "first_name": "John",
            "last_name": "Doe"
        }
        jsonld_dict = json.loads(mt.model_dump_jsonld(resolve_keys=False))
        jsonld_dict.pop('@id')
        self.assertDictEqual(jsonld_dict,
                             ref_jsonld)
        from pprint import pprint
        pprint(jsonld_dict)
