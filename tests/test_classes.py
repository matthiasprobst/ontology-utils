import datetime
import json
import logging
import unittest
from typing import Optional

import pydantic
import rdflib
from pydantic import EmailStr, model_validator
from pydantic import field_validator, Field
from rdflib.plugins.shared.jsonld.context import Context

from ontolutils import Thing, urirefs, namespaces, get_urirefs, get_namespaces
from ontolutils import as_id
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

    def test_model_fields(self):
        @namespaces(foaf="http://xmlns.com/foaf/0.1/")
        @urirefs(Agent='foaf:Agent',
                 name='foaf:lastName',
                 age='foaf:age')
        class Agent(Thing):
            """Pydantic Model for http://xmlns.com/foaf/0.1/Agent
            Parameters
            ----------
            mbox: EmailStr = None
                Email address (foaf:mbox)
            """
            name: str = Field(default=None, alias="lastName")  # name is synonymous to lastName
            age: int = None
            special_field: Optional[str] = None

            @field_validator('special_field', mode="before")
            @classmethod
            def _special_field(cls, value):
                assert value == "special_string", f"Special field must be 'special_string' not {value}"
                return value

        agent = Agent(name='John Doe', age=23)
        self.assertEqual(agent.name, 'John Doe')
        self.assertEqual(agent.age, 23)

        # extra fields are allowed and either the model field or its uriref can be used
        agent = Agent(lastName='Doe', age=23)
        self.assertEqual(agent.name, 'Doe')
        self.assertEqual(agent.lastName, 'Doe')
        self.assertEqual(agent.age, 23)

        agent = Agent(age=23)
        self.assertEqual(agent.name, None)
        self.assertEqual(agent.age, 23)

        # property assignment should fail:
        with self.assertRaises(pydantic.ValidationError):
            agent.age = "invalid"

        with self.assertRaises(pydantic.ValidationError):
            agent.special_field = "invalid"
        self.assertEqual(agent.special_field, None)

        agent.special_field = "special_string"
        self.assertEqual(agent.special_field, "special_string")

    def test_resolve_iri(self):
        ret = resolve_iri('foaf:age', context=Context(source={'foaf': 'http://xmlns.com/foaf/0.1/'}))
        self.assertEqual(ret, 'http://xmlns.com/foaf/0.1/age')

        ret = resolve_iri('age', context=Context(source={'foaf': 'http://xmlns.com/foaf/0.1/'}))
        self.assertEqual(ret, None)

        ret = resolve_iri('age', context=Context(source={'age': 'http://xmlns.com/foaf/0.1/age'}))
        self.assertEqual(ret, 'http://xmlns.com/foaf/0.1/age')

        ret = resolve_iri('label', context=Context(source={'age': 'http://xmlns.com/foaf/0.1/age'}))
        self.assertEqual(ret, 'http://www.w3.org/2000/01/rdf-schema#label')

        ret = resolve_iri('label',
                          context=Context(source={'label': {'@id': 'http://www.w3.org/2000/01/rdf-schema#label'}}))
        self.assertEqual(ret, 'http://www.w3.org/2000/01/rdf-schema#label')

        ret = resolve_iri('prefix:label', Context(source={}))
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
                    schema='http://www.schema.org/')
        @urirefs(Affiliation='prov:Affiliation',
                 name='schema:name')
        class Affiliation(Thing):
            name: str

        @namespaces(foaf='http://xmlns.com/foaf/0.1/',
                    prov='http://www.w3.org/ns/prov#')
        @urirefs(Person='prov:Person',
                 first_name='foaf:firstName',
                 lastName='foaf:lastName',
                 age='foaf:age')
        class Person(Thing):
            first_name: str = Field(default=None, alias='firstName')
            lastName: str
            age: int = None
            affiliation: Affiliation = None

        p = Person(first_name='John', lastName='Doe', age=23)
        person_json = p.model_dump_jsonld(resolve_keys=False)
        self.assertEqual(json.loads(person_json)['first_name'], 'John')
        person_json = p.model_dump_jsonld(resolve_keys=True)
        self.assertEqual(json.loads(person_json)['foaf:firstName'], 'John')

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

    def test_from_jsonld_for_nested_objects(self):
        @namespaces(prov='http://www.w3.org/ns/prov#')
        @urirefs(A='prov:A',
                 name='prov:name')
        class A(Thing):
            name: str = None

        @namespaces(prov='http://www.w3.org/ns/prov#')
        @urirefs(B='prov:B',
                 a='prov:a')
        class B(Thing):
            a: A = None

        @namespaces(prov='http://www.w3.org/ns/prov#')
        @urirefs(C='prov:C',
                 b='prov:b')
        class C(Thing):
            b: B = None

        @namespaces(prov='http://www.w3.org/ns/prov#')
        @urirefs(D='prov:D',
                 c='prov:c')
        class D(Thing):
            c: C = None

        aj = A(name="myname").model_dump_jsonld()
        an = A.from_jsonld(data=aj, limit=1)
        self.assertEqual("myname", an.name)

        bj = B(a=(A(name="myname"))).model_dump_jsonld()
        bn = B.from_jsonld(data=bj, limit=1)
        self.assertEqual("myname", bn.a.name)

        cj = C(b=B(a=(A(name="myname")))).model_dump_jsonld()
        cn = C.from_jsonld(data=cj, limit=1)
        self.assertEqual("myname", cn.b.a.name)

        dj = D(c=C(b=B(a=(A(name="myname"))))).model_dump_jsonld()
        dn = D.from_jsonld(data=dj, limit=1)
        self.assertEqual("myname", dn.c.b.a.name)

    def test_sort_classes(self):
        thing1 = Thing(label='Thing 1', id='_:1')
        thing2 = Thing(label='Thing 2', id='_:2')
        self.assertFalse(thing1 > thing2)
        with self.assertRaises(TypeError):
            thing1 < 4
        thing1 = Thing(label='Thing 1', id='http://example.com/thing1')
        thing2 = Thing(label='Thing 2', id='http://example.com/thing2')
        self.assertTrue(thing1 < thing2)

    def test__repr_html_(self):
        thing = Thing(label='Thing 1')
        self.assertEqual(thing._repr_html_(), f'Thing(id={thing.id}, label=Thing 1)')

    def test_thing_get_jsonld_dict(self):
        with self.assertRaises(pydantic.ValidationError):
            _ = Thing(id=1, label='Thing 1')

        thing = Thing(id='https://example.org/TestThing', label='Test Thing', numerical_value=1.0,
                      dt=datetime.datetime(2021, 1, 1))
        with self.assertRaises(TypeError):
            thing.get_jsonld_dict(context=1)

        thing_dict = thing.get_jsonld_dict(resolve_keys=True)
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
        self.assertTrue('@id' in json.loads(jsonld_str1))

        self.assertIsInstance(json.loads(jsonld_str1)['foaf:age'], int)

        jsonld_str2 = agent.model_dump_jsonld(rdflib_serialize=True)  # will assign blank node! Pop it later
        jsonld_str2_dict = json.loads(jsonld_str2)
        self.assertDictEqual(
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
        self.assertNotEqual(agent.id, None)
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

        # do the same with thing:
        thing = Thing.from_jsonld(data=jsonld_string, limit=1)
        self.assertEqual(thing.label, 'Agent 1')
        self.assertTrue(thing.id.startswith('_:'))
        _id = thing.id

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
        jsonld_str = person.model_dump_jsonld(resolve_keys=True)
        jsonld_dict = json.loads(jsonld_str)

        self.assertEqual(jsonld_dict['schema:affiliation']['@type'], 'prov:Organization')
        self.assertEqual(jsonld_dict['schema:affiliation']['rdfs:label'], 'Organization 1')
        self.assertEqual(jsonld_dict['rdfs:label'], 'Person 1')
        self.assertEqual(jsonld_dict['@type'], 'foaf:Person')

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

    def test_use_as_id(self):
        @namespaces(prov="http://www.w3.org/ns/prov#",
                    foaf="http://xmlns.com/foaf/0.1/",
                    m4i="http://w3id.org/nfdi4ing/metadata4ing#"
                    )
        @urirefs(Person='prov:Person',
                 firstName='foaf:firstName',
                 lastName='foaf:lastName',
                 orcidId='m4i:orcidId',
                 mbox='foaf:mbox')
        class Person(Thing):
            firstName: str
            lastName: str = None
            mbox: EmailStr = None
            orcidId: str = Field(default=None, alias="orcid_id")

            @model_validator(mode="before")
            def _change_id(self):
                return as_id(self, "orcidId")

        p = Person(
            id="local:cde4c79c-21f2-4ab7-b01d-28de6e4aade4",
            firstName='John',
            lastName='Doe',
            orcidId='https://orcid.org/0000-0001-8729-0482', )
        jsonld = {
            "@context": {
                'm4i': 'http://w3id.org/nfdi4ing/metadata4ing#',
                "owl": "http://www.w3.org/2002/07/owl#",
                "prov": "http://www.w3.org/ns/prov#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "foaf": "http://xmlns.com/foaf/0.1/",
            },
            "@type": "prov:Person",
            "foaf:firstName": "John",
            "foaf:lastName": "Doe",
            "m4i:orcidId": "https://orcid.org/0000-0001-8729-0482",
            "@id": "https://orcid.org/0000-0001-8729-0482",
        }

        self.assertDictEqual(json.loads(p.model_dump_jsonld()),
                             jsonld)

    def test_use_as_id_V2(self):
        @namespaces(schema="https://schema.org/",
                    foaf="http://xmlns.com/foaf/0.1/",
                    )
        @urirefs(Orga='prov:Organization',
                 name="schema:name",
                 identifier="schema:identifier",
                 mbox='foaf:mbox')
        class Orga(Thing):
            identifier: str = Field(default=None, alias="identifier")
            name: str = Field(default=None, alias="name")
            mbox: EmailStr = None

            @model_validator(mode="before")
            def _change_id(self):
                return as_id(self, "identifier")

        @namespaces(prov="http://www.w3.org/ns/prov#",
                    foaf="http://xmlns.com/foaf/0.1/",
                    m4i="http://w3id.org/nfdi4ing/metadata4ing#"
                    )
        @urirefs(Person='prov:Person',
                 firstName='foaf:firstName',
                 lastName='foaf:lastName',
                 orcidId='m4i:orcidId',
                 mbox='foaf:mbox')
        class Person(Thing):
            firstName: str
            lastName: str = None
            mbox: EmailStr = None
            orcidId: str = Field(default=None, alias="orcid_id")
            affiliation: Orga = None

            @model_validator(mode="before")
            def _change_id(self):
                return as_id(self, "orcidId")

        with self.assertRaises(ValueError):
            p = Person(
                id="local:cde4c79c-21f2-4ab7-b01d-28de6e4aade4",
                firstName='John',
                lastName='Doe',
                orcidId='https://orcid.org/0000-0001-8729-0482',
                affiliation=Orga(identifier='123', name='Orga 1')
            )
        p = Person(
            id="local:cde4c79c-21f2-4ab7-b01d-28de6e4aade4",
            firstName='John',
            lastName='Doe',
            orcidId='https://orcid.org/0000-0001-8729-0482',
            affiliation=Orga(identifier='https://example.org/123', name='Orga 1')
        )
        pdict = json.loads(p.model_dump_jsonld())
        assert pdict['@id'] == 'https://orcid.org/0000-0001-8729-0482'
        assert pdict['affiliation']["@id"] == 'https://example.org/123'

    def test_use_as_id_V3(self):
        @namespaces(schema="https://schema.org/",
                    foaf="http://xmlns.com/foaf/0.1/",
                    )
        @urirefs(Orga='prov:Organization',
                 name="schema:name",
                 identifier="schema:identifier",
                 mbox='foaf:mbox')
        class Orga(Thing):
            identifier: str = Field(default=None, alias="identifier")
            name: str = Field(default=None, alias="name")
            mbox: EmailStr = None

            @model_validator(mode="after")
            def _change_id(self):
                return as_id(self, "identifier")

        @namespaces(prov="http://www.w3.org/ns/prov#",
                    foaf="http://xmlns.com/foaf/0.1/",
                    m4i="http://w3id.org/nfdi4ing/metadata4ing#"
                    )
        @urirefs(Person='prov:Person',
                 firstName='foaf:firstName',
                 lastName='foaf:lastName',
                 orcidId='m4i:orcidId',
                 mbox='foaf:mbox')
        class Person(Thing):
            firstName: str
            lastName: str = None
            mbox: EmailStr = None
            orcidId: str = Field(default=None, alias="orcid_id")
            affiliation: Orga = None

            @model_validator(mode="before")
            def _change_id(self):
                return as_id(self, "orcidId")

        with self.assertRaises(ValueError):
            Person(
                id="local:cde4c79c-21f2-4ab7-b01d-28de6e4aade4",
                firstName='John',
                lastName='Doe',
                orcidId='https://orcid.org/0000-0001-8729-0482',
                affiliation=Orga(identifier='123', name='Orga 1')
            )

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
        jsonld_dict = json.loads(mt.model_dump_jsonld())
        jsonld_dict.pop('@id', None)
        self.assertDictEqual(jsonld_dict,
                             ref_jsonld)

        jsonld_dict = json.loads(mt.model_dump_jsonld())
        jsonld_dict.pop('@id', None)
        self.assertDictEqual(jsonld_dict,
                             ref_jsonld)
