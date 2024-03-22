import json
import logging
import pydantic
import unittest
from pydantic import EmailStr

from ontolutils import Thing, urirefs, namespaces, get_urirefs, get_namespaces
from ontolutils import set_logging_level
from ontolutils.classes import decorator

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

    def test_thing_custom_prop(self):
        """It is helpful to have the properties equal to the urirefs keys,
        however, this should not be required!"""

        @namespaces(foaf='http://xmlns.com/foaf/0.1/',
                    prov='http://www.w3.org/ns/prov#')
        @urirefs(Person='prov:Person',
                 first_name='foaf:firstName',
                 lastName='foaf:lastName')
        class Person(Thing):
            first_name: str = None
            lastName: str

        p = Person(first_name='John', lastName='Doe')
        print(p.model_dump_jsonld(resolve_keys=False))

    def test_sort_classes(self):
        thing1 = Thing(label='Thing 1')
        thing2 = Thing(label='Thing 2')
        self.assertFalse(thing1 < thing2)
        with self.assertRaises(TypeError):
            thing1 < 4
        thing1 = Thing(label='Thing 1', id='http://example.com/thing1')
        thing2 = Thing(label='Thing 2', id='http://example.com/thing2')
        self.assertTrue(thing1 < thing2)

    # def test_serialize_fields(self):
    #     from ontolutils.classes.thing import serialize_fields
    #     self.assertEqual(serialize_fields(1), 1)
    #     self.assertEqual(serialize_fields(1.1), 1.1)
    #     self.assertEqual(serialize_fields('1'), '1')
    #     self.assertEqual(serialize_fields(True), True)
    #     thing = Thing(label='Thing 1')
    #
    #     class RandomClass:
    #         """Random Class"""
    #
    #     rc = RandomClass()
    #     self.assertEqual(serialize_fields(rc), rc)
    #
    #     self.assertDictEqual(serialize_fields(Thing(id='_:b1', label='Thing 1')),
    #                          {'@type': 'owl:Thing', 'rdfs:label': 'Thing 1', '@id': '_:b1'})
    #
    #     @namespaces(owl='http://www.w3.org/2002/07/owl#',
    #                 local='http://example.org/')
    #     @urirefs(Process='local:Process',
    #              startTime='local:startTime',
    #              listOfTimes='local:listOfTimes')
    #     class Process(Thing):
    #         """Process Thing"""
    #         startTime: datetime.datetime = None
    #         listOfTimes: List[datetime.datetime] = None
    #
    #     process = Process(id='_:b1', label='Process 1',
    #                       startTime=datetime.datetime(2021, 1, 1))
    #     self.assertEqual(serialize_fields(process),
    #                      {'@type': 'local:Process', 'rdfs:label': 'Process 1', 'local:startTime': '2021-01-01T00:00:00',
    #                       '@id': '_:b1'})
    #
    #     process = Process(id='_:b1',
    #                       label='Process 1',
    #                       listOfTimes=[datetime.datetime(2021, 1, 1),
    #                                    datetime.datetime(2021, 1, 2)])
    #
    #     self.assertEqual(serialize_fields(process),
    #                      {'@type': 'local:Process', 'rdfs:label': 'Process 1',
    #                       'local:listOfTimes': ['2021-01-01T00:00:00', '2021-01-02T00:00:00'],
    #                       '@id': '_:b1'})

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
