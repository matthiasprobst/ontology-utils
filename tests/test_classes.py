import datetime
import json
import logging
import unittest
from itertools import count
from typing import Optional, List, Union

import pydantic
import rdflib
from pydantic import EmailStr, model_validator
from pydantic import ValidationError
from pydantic import field_validator, Field
from rdflib.plugins.shared.jsonld.context import Context
from typing_extensions import Annotated

import ontolutils
from ontolutils import Thing, urirefs, namespaces, build, Property
from ontolutils import as_id
from ontolutils import get_urirefs, get_namespaces, set_config
from ontolutils import set_logging_level
from ontolutils.classes import decorator
from ontolutils.classes.thing import resolve_iri, LangString
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
        self.assertListEqual(split_URIRef(rdflib.URIRef('https://example.com/')),
                             ['https://example.com/', ''])
        self.assertListEqual(split_URIRef(rdflib.URIRef('https://example.com/#test')),
                             ['https://example.com/#', 'test'])
        self.assertListEqual(split_URIRef(rdflib.URIRef('https://example.com/test')),
                             ['https://example.com/', 'test'])
        self.assertListEqual(split_URIRef(rdflib.URIRef('https://example.com/test#test')),
                             ['https://example.com/test#', 'test'])
        self.assertListEqual(split_URIRef(rdflib.URIRef('https://example.com/test:123')),
                             ['https://example.com/', 'test:123'])

    def test_thing_custom_prop(self):
        """It is helpful to have the properties equal to the urirefs keys,
        however, this should not be required!"""

        @namespaces(foaf='http://xmlns.com/foaf/0.1/',
                    schema='https://www.schema.org/')
        @urirefs(Affiliation='prov:Affiliation',
                 name='schema:name')
        class Affiliation(Thing):
            name: str

        @namespaces(foaf='http://xmlns.com/foaf/0.1/',
                    prov='https://www.w3.org/ns/prov#')
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
        @namespaces(prov='https://www.w3.org/ns/prov#')
        @urirefs(A='prov:A',
                 name='prov:name')
        class A(Thing):
            name: str = None

        @namespaces(prov='https://www.w3.org/ns/prov#')
        @urirefs(B='prov:B',
                 a='prov:a')
        class B(Thing):
            a: A = None

        @namespaces(prov='https://www.w3.org/ns/prov#')
        @urirefs(C='prov:C',
                 b='prov:b')
        class C(Thing):
            b: B = None

        @namespaces(prov='https://www.w3.org/ns/prov#')
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
        thing1 = Thing(label='Thing 1', id='https://example.com/thing1')
        thing2 = Thing(label='Thing 2', id='https://example.com/thing2')
        self.assertTrue(thing1 < thing2)

    def test_language(self):
        self.assertEqual("a thing", LangString(value="a thing", lang="en").value)
        self.assertEqual("a thing", LangString(value="a thing").value)
        self.assertNotEqual("a thing", LangString(value="another thing", lang="en").value)

        thing_en = Thing(label=LangString(value='a thing.', lang='en'))
        ttl = thing_en.model_dump_ttl()
        self.assertEqual(ttl, """@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

[] a owl:Thing ;
    rdfs:label "a thing."@en .

""")

        thing_en = Thing(label="deutsch@de")
        ttl = thing_en.model_dump_ttl()
        self.assertEqual(ttl, """@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

[] a owl:Thing ;
    rdfs:label "deutsch"@de .

""")

        #         thing_en = Thing(label=LangString(value='2025-01-01', datatype=XSD.date))
        #         ttl = thing_en.model_dump_ttl()
        #         self.assertEqual(ttl, """@prefix owl: <http://www.w3.org/2002/07/owl#> .
        # @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        # @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        #
        # [] a owl:Thing ;
        #     rdfs:label "2025-01-01"^^xsd:date .
        #
        # """)

        thing_en = Thing(label='2025-01-01')
        ttl = thing_en.model_dump_ttl()
        self.assertEqual(ttl, """@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

[] a owl:Thing ;
    rdfs:label "2025-01-01" .

""")

    def test__repr_html_(self):
        thing = Thing(label='Thing 1')
        self.assertEqual(thing._repr_html_(), f'Thing(id={thing.id}, label=Thing 1)')

    def test_thing_get_jsonld_dict(self):
        with self.assertRaises(TypeError):
            _ = Thing(id=1, label='Thing 1')
        with self.assertRaises(pydantic.ValidationError):
            _ = Thing(id="1", label='Thing 1')

        thing = Thing(id='https://example.org/TestThing', label='Test Thing', numerical_value=1.0,
                      dt=datetime.datetime(2021, 1, 1))
        with self.assertRaises(TypeError):
            thing.get_jsonld_dict(context=1, base_uri=None)

        thing_dict = thing.get_jsonld_dict(
            resolve_keys=True,
            exclude_none=True,
            base_uri=None,
            context=None
        )
        self.assertIsInstance(thing_dict, dict)
        self.assertDictEqual(
            thing_dict['@context'],
            {'owl': 'http://www.w3.org/2002/07/owl#',
             'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
             'skos': 'http://www.w3.org/2004/02/skos/core#',
             'dcterms': 'http://purl.org/dc/terms/'
             }
        )

        self.assertEqual(thing_dict['@id'], 'https://example.org/TestThing')
        self.assertEqual(thing_dict['rdfs:label'], 'Test Thing')
        self.assertEqual(thing_dict['@type'], 'owl:Thing')

    def test_decorator(self):
        self.assertTrue(decorator._is_http_url('https://example.com/'))
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

        def base_uri_generator():
            return f"https://example.org/agents/{rdflib.BNode()}"

        with set_config(blank_id_generator=base_uri_generator):
            new_agent = Agent(
                label='Agent new',
                mbox='new_agent@email.com',
                age=33, )
            jsonld_with_base_uri = new_agent.model_dump_jsonld()
        self.assertTrue(
            Agent.from_jsonld(data=jsonld_with_base_uri, limit=1).id.startswith("https://example.org/agents/"))

        new_agent = Agent(
            label='Agent new',
            mbox='new_agent@email.com',
            age=33, )
        jsonld_with_blank_node_base_uri = new_agent.model_dump_jsonld()
        self.assertTrue(Agent.from_jsonld(data=jsonld_with_blank_node_base_uri, limit=1).id.startswith("_:"))

        jsonld_with_base_uri = new_agent.model_dump_jsonld(base_uri="https://example.org/agents/")
        self.assertTrue(
            Agent.from_jsonld(data=jsonld_with_base_uri, limit=1).id.startswith("https://example.org/agents/"))

        new_agent = Agent(
            id="https://example.org/agents/new_agent/123",
            label='Agent new',
            mbox='new_agent@email.com',
            age=33, )
        new_agent_jsonld = new_agent.model_dump_jsonld()
        self.assertEqual(Agent.from_jsonld(data=new_agent_jsonld, limit=1).id,
                         "https://example.org/agents/new_agent/123")

        new_agent_jsonld = new_agent.model_dump_jsonld(base_uri="https://example.org/agents/")
        self.assertEqual(Agent.from_jsonld(data=new_agent_jsonld, limit=1).id,
                         "https://example.org/agents/new_agent/123")

        new_agent = Agent(
            id="_:123",
            label='Agent new',
            mbox='new_agent@email.com',
            age=33, )
        new_agent_jsonld = new_agent.model_dump_jsonld(base_uri="https://example.org/agents/")
        self.assertEqual(Agent.from_jsonld(data=new_agent_jsonld, limit=1).id,
                         "https://example.org/agents/123")

    def test_model_dump_ttl(self):
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
        self.assertEqual(
            """@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

[] a foaf:Agent ;
    rdfs:label "Agent 1" ;
    foaf:age 23 ;
    foaf:mbox "my@email.com" .

""",
            agent.model_dump_ttl()
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
        self.assertEqual(thing.label, LangString(value="Agent 1"))
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
        @namespaces(prov="https://www.w3.org/ns/prov#",
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
            id="_:cde4c79c-21f2-4ab7-b01d-28de6e4aade4",
            firstName='John',
            lastName='Doe',
            orcidId='https://orcid.org/0000-0001-8729-0482', )
        jsonld = {
            "@context": {
                'm4i': 'http://w3id.org/nfdi4ing/metadata4ing#',
                "owl": "http://www.w3.org/2002/07/owl#",
                "prov": "https://www.w3.org/ns/prov#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "dcterms": "http://purl.org/dc/terms/",
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "foaf": "http://xmlns.com/foaf/0.1/",
            },
            "@type": "prov:Person",
            "foaf:firstName": "John",
            "foaf:lastName": "Doe",
            "m4i:orcidId": {"@id": "https://orcid.org/0000-0001-8729-0482"},
            "@id": "_:cde4c79c-21f2-4ab7-b01d-28de6e4aade4",
        }

        self.assertDictEqual(json.loads(p.model_dump_jsonld()),
                             jsonld)

        p_without_http_orcid = Person(
            firstName='John',
            lastName='Doe',
            orcidId='0000-0001-8729-0482')
        self.assertEqual(json.loads(p_without_http_orcid.model_dump_jsonld())["@id"],
                         p_without_http_orcid.id)
        self.assertEqual(json.loads(p_without_http_orcid.model_dump_jsonld())["m4i:orcidId"],
                         '0000-0001-8729-0482')

        p = Person(
            firstName='John',
            lastName='Doe',
            orcidId='https://orcid.org/0000-0001-8729-0482', )
        jsonld = {
            "@context": {
                'm4i': 'http://w3id.org/nfdi4ing/metadata4ing#',
                "owl": "http://www.w3.org/2002/07/owl#",
                "prov": "https://www.w3.org/ns/prov#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "dcterms": "http://purl.org/dc/terms/",
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "foaf": "http://xmlns.com/foaf/0.1/",
            },
            "@type": "prov:Person",
            "foaf:firstName": "John",
            "foaf:lastName": "Doe",
            "m4i:orcidId": {"@id": "https://orcid.org/0000-0001-8729-0482"},
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

        @namespaces(prov="https://www.w3.org/ns/prov#",
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

        p = Person(
            id="_:cde4c79c-21f2-4ab7-b01d-28de6e4aade4",
            firstName='John',
            lastName='Doe',
            orcidId='https://orcid.org/0000-0001-8729-0482',
            affiliation=Orga(identifier='https://example.org/123', name='Orga 1')
        )
        # Person was created with an explicit ID
        self.assertEqual(p.id, "_:cde4c79c-21f2-4ab7-b01d-28de6e4aade4")

        p = Person(
            firstName='John',
            lastName='Doe',
            orcidId='https://orcid.org/0000-0001-8729-0482',
            affiliation=Orga(identifier='https://example.org/123', name='Orga 1')
        )

        pdict = json.loads(p.model_dump_jsonld())
        self.assertEqual(pdict['@id'], 'https://orcid.org/0000-0001-8729-0482')
        self.assertEqual(pdict['affiliation']["@id"], 'https://example.org/123')

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

        @namespaces(prov="https://www.w3.org/ns/prov#",
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
                id="_:cde4c79c-21f2-4ab7-b01d-28de6e4aade4",
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
        self.assertDictEqual(mt.urirefs,
                             {'Thing': 'owl:Thing', 'closeMatch': 'skos:closeMatch', 'exactMatch': 'skos:exactMatch',
                              'label': 'rdfs:label', 'relation': 'dcterms:relation'})
        self.assertDictEqual(mt.namespaces, get_namespaces(Thing))
        self.assertDictEqual(mt.namespaces, {'owl': 'http://www.w3.org/2002/07/owl#',
                                             'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
                                             'skos': 'http://www.w3.org/2004/02/skos/core#',
                                             'dcterms': 'http://purl.org/dc/terms/'})

        mt = CustomPerson(first_name='John', last_name='Doe')
        with self.assertRaises(AttributeError):
            mt.namespaces = 'http://xmlns.com/foaf/0.1/'
        with self.assertRaises(AttributeError):
            mt.urirefs = 'foaf:lastName'

        mt.namespaces['foaf'] = 'http://xmlns.com/foaf/0.1/'
        mt.urirefs['first_name'] = 'foaf:firstName'
        mt.urirefs['last_name'] = 'foaf:lastName'

        ref_jsonld = {
            "@context": {
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "dcterms": "http://purl.org/dc/terms/",
                "skos": "http://www.w3.org/2004/02/skos/core#",
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

    def test_blank_id_generator(self):
        @namespaces(foaf='http://xmlns.com/foaf/0.1/',
                    prov='https://www.w3.org/ns/prov#')
        @urirefs(Person='prov:Person',
                 first_name='foaf:firstName')
        class Person(Thing):
            first_name: str = Field(default=None, alias='firstName')

        counter = count()

        def my_generator():
            return f"_:{next(counter)}"

        with set_config(blank_id_generator=my_generator):
            p = Person(firstName="John")
            self.assertEqual("_:0", p.id)
            p = Person(firstName="John")
            self.assertEqual("_:1", p.id)

    def test_blank_node_prefix(self):
        @namespaces(foaf='http://xmlns.com/foaf/0.1/',
                    prov='https://www.w3.org/ns/prov#')
        @urirefs(Person='prov:Person',
                 first_name='foaf:firstName')
        class Person(Thing):
            first_name: str = Field(default=None, alias='firstName')

        p = Person(firstName="John")
        self.assertTrue(p.id.startswith("_:"))

        p = Person(firstName="John")
        self.assertTrue(p.id.startswith("_:"))

    def test_dynamic_thing(self):
        MyThing = build(
            namespace="https://schema.org/",
            namespace_prefix="schema",
            class_name="MyThing",
            properties=[Property(
                name="about",
                default=None,
                property_type=str
            )]
        )
        mything = MyThing(about="my thing")
        self.assertEqual(mything.about, "my thing")

    def test_dynamic_thing_with_validator(self):
        def validate_str(cls, value):
            if "thing" not in value:
                raise ValueError("Value must contain 'thing'")
            return value

        PositiveInt = Annotated[int, Field(gt=0)]

        MySpecialThing = build(
            baseclass=Thing,
            namespace="https://schema.org/",
            namespace_prefix="schema",
            class_name="MyThing",
            properties=[Property(
                name="value",
                default=Field(default=None, alias="val"),
                property_type=PositiveInt
            )]
        )
        with self.assertRaises(ValidationError):
            MySpecialThing(value=-1)
        mst = MySpecialThing(value=3)
        self.assertEqual(mst.value, 3)
        mst = MySpecialThing(val=4)
        self.assertEqual(mst.value, 4)

        MySpecialThing2 = Thing.build(
            namespace="https://schema.org/",
            namespace_prefix="schema",
            class_name="MyThing",
            properties=[Property(
                name="value",
                default=Field(default=None, alias="val"),
                property_type=PositiveInt
            )]
        )
        with self.assertRaises(ValidationError):
            MySpecialThing2(value=-1)
        mst = MySpecialThing2(value=3)
        self.assertEqual(mst.value, 3)
        mst = MySpecialThing2(val=4)
        self.assertEqual(mst.value, 4)

        NegativeInt = Annotated[int, Field(lt=0)]
        MySubSpecialThing = MySpecialThing.build(
            namespace="https://schema.org/",
            namespace_prefix="schema",
            class_name="MySubSpecialThing",
            properties=[Property(
                name="negValue",
                default=Field(default=None, alias="nval"),
                property_type=NegativeInt
            )]
        )
        with self.assertRaises(ValidationError):
            MySubSpecialThing(negValue=1)
        self.assertIsInstance(MySubSpecialThing(negValue=-1), MySubSpecialThing)
        mst = MySubSpecialThing(negValue=-3)
        self.assertEqual(mst.negValue, -3)
        self.assertEqual(mst.value, None)
        mst = MySubSpecialThing(nval=-4)
        self.assertEqual(mst.negValue, -4)

    def test_dynamic_forward_references(self):
        Person = Thing.build(
            namespace="https://example.org/",
            namespace_prefix="ex",
            class_name="Person",
            properties=[
                Property(
                    name="name",
                    default=None,
                    property_type=str
                ),
                Property(
                    name="friends",
                    default=None,
                    property_type=List["Person"]
                )
            ]
        )
        person1 = Person(name="John")
        person2 = Person(name="Jane", friends=[person1])
        expected_serialization = """@prefix ex: <https://example.org/> .

[] a ex:Person ;
    ex:friends [ a ex:Person ;
            ex:name "John" ] ;
    ex:name "Jane" .

"""
        self.assertEqual(expected_serialization, person2.serialize("ttl"))

    def test_skos_fields(self):
        @namespaces(foaf="http://xmlns.com/foaf/0.1/")
        @urirefs(Agent='foaf:Agent',
                 name='foaf:lastName',
                 age='foaf:age')
        class Agent(Thing):
            name: str = Field(default=None, alias="lastName")  # name is synonymous to lastName
            age: int = None
            special_field: Optional[str] = None

        a = Agent(name='John Doe', age=23)
        b = Agent(name='John Doe', age=23)
        a.exactMatch = b
        expected_ttl = """@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

[] a foaf:Agent ;
    skos:exactMatch [ a foaf:Agent ;
            foaf:age 23 ;
            foaf:lastName "John Doe" ] ;
    foaf:age 23 ;
    foaf:lastName "John Doe" .

"""
        self.assertEqual(expected_ttl, a.serialize(format="ttl"))

        a = Agent(id="https://example.org/jd", name='John Doe', age=23)
        b = Agent(name='John Doe', age=23, closeMatch=a.id)

        expected_ttl = """@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

[] a foaf:Agent ;
    skos:closeMatch <https://example.org/jd> ;
    foaf:age 23 ;
    foaf:lastName "John Doe" .

"""
        self.assertEqual(expected_ttl, b.serialize(format="ttl"))

    def test_behaviour_of_non_specified_fields(self):
        # if a Thing has not specified a specific field, but a user sets it, it cannot be validated, however,
        # if the user somehow passes the URI of the field, it should be accepted.

        @namespaces(foaf="http://xmlns.com/foaf/0.1/")
        @urirefs(Agent='foaf:Agent',
                 name='foaf:lastName',
                 age='foaf:age')
        class Agent(Thing):
            name: str = Field(default=None, alias="lastName")  # name is synonymous to lastName
            age: int = None

        # in the following, home_town is not specified in the Agent class, but we set it anyway
        a = Agent(name='John Doe', age=23, homeTown=ontolutils.URIValue("Berlin", "http://example.org", "ex"))

    def test_relation(self):
        @namespaces(foaf="http://xmlns.com/foaf/0.1/")
        @urirefs(Agent='foaf:Agent',
                 name='foaf:lastName',
                 age='foaf:age')
        class Agent(Thing):
            name: str = Field(default=None, alias="lastName")  # name is synonymous to lastName
            age: int = None
            special_field: Optional[str] = None

        a = Agent(name='John Doe', age=23, relation="https://example.org/123")

        expected_ttl = """@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

[] a foaf:Agent ;
    dcterms:relation <https://example.org/123> ;
    foaf:age 23 ;
    foaf:lastName "John Doe" .

"""
        with self.assertRaises(ValueError):
            a = Agent(id="agents/123", name='John Doe', age=23, relation="https://example.org/123")

        a = Agent(id="_:agents/123", name='John Doe', age=23, relation="https://example.org/123")
        self.assertEqual(expected_ttl, a.serialize(format="ttl"))

        expected_ttl_with_base_uri = """@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://example.org/agents/123> a foaf:Agent ;
    dcterms:relation <https://example.org/123> ;
    foaf:age 23 ;
    foaf:lastName "John Doe" .

"""
        self.assertEqual(expected_ttl_with_base_uri, a.serialize(format="ttl", base_uri="https://example.org/"))

        expected_ttl_with_base_uri2 = """@prefix agents: <https://example.org/agents/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

agents:123 a foaf:Agent ;
    dcterms:relation <https://example.org/123> ;
    foaf:age 23 ;
    foaf:lastName "John Doe" .

"""
        self.assertEqual(
            expected_ttl_with_base_uri2,
            a.serialize(format="ttl", base_uri="https://example.org/",
                        context={"agents": "https://example.org/agents/"})
        )

    def test_different_python_classes_same_uri(self):
        @namespaces(foaf='http://xmlns.com/foaf/0.1/',
                    prov='https://www.w3.org/ns/prov#')
        @urirefs(Person1='prov:Person',
                 first_name='foaf:firstName')
        class Person1(Thing):
            first_name: str = Field(default=None, alias='firstName')

        p1 = Person1(first_name='John')
        self.assertEqual(p1.namespace, "https://www.w3.org/ns/prov#")
        self.assertEqual(p1.uri, "https://www.w3.org/ns/prov#Person")

        @namespaces(foaf='http://xmlns.com/foaf/0.1/',
                    prov='https://www.w3.org/ns/prov#')
        @urirefs(Person2='prov:Person',
                 first_name='foaf:firstName',
                 last_name='foaf:lastName')
        class Person2(Thing):
            first_name: str = Field(alias='firstName')
            last_name: str = Field(alias='lastName')

        p1 = Person1(first_name='John')
        p2 = Person2(first_name='John', last_name="Doe")
        self.assertNotEqual(p1, p2)
        self.assertEqual(p1.namespace, p2.namespace)

        p1_from_p2 = p2.map(Person1)
        self.assertIsInstance(p1_from_p2, Thing)
        self.assertIsInstance(p1_from_p2, Person1)
        self.assertEqual(p1_from_p2.first_name, 'John')
        self.assertEqual(p1_from_p2.last_name, 'Doe')
        jsonld_dict = json.loads(p1_from_p2.model_dump_jsonld())
        self.assertTrue("foaf:lastName" in jsonld_dict)

        @namespaces(ex='http://example.org/',
                    prov='https://www.w3.org/ns/prov#')
        @urirefs(Organization='ex:Organization',
                 members='prov:Person')
        class Organization(Thing):
            members: Union[Person1, List[Person1]]

        # it should be irrelevant which Person class is taken, unless the uri is different
        org1 = Organization(members=p1)
        org2 = Organization(members=p2.map(Person1))
        # org3 = Organization(members=[p1, p2])
