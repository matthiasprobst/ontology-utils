"""Testing code used in the README.md file"""
import json
import unittest
from typing import List, Union

from pydantic import EmailStr, Field
from pydantic import HttpUrl, model_validator

from ontolutils import build, Property, Thing
from ontolutils import urirefs, namespaces, as_id


class TestReadmeCode(unittest.TestCase):

    def test_code1_on_readme(self):
        """Just has to run without errors"""

        @namespaces(prov="https://www.w3.org/ns/prov#",
                    foaf="https://xmlns.com/foaf/0.1/",
                    m4i='http://w3id.org/nfdi4ing/metadata4ing#')
        @urirefs(Person='prov:Person',
                 firstName='foaf:firstName',
                 lastName='foaf:lastName',
                 mbox='foaf:mbox',
                 orcidId='m4i:orcidId')
        class Person(Thing):
            firstName: str
            lastName: str = Field(default=None, alias="last_name")  # you may provide an alias
            mbox: EmailStr = Field(default=None, alias="email")
            orcidId: HttpUrl = Field(default=None, alias="orcid_id")

            # the following will ensure, that if orcidId is set, it will be used as the id
            @model_validator(mode="before")
            def _change_id(self):
                return as_id(self, "orcidId")

        p = Person(id="https://orcid.org/0000-0001-8729-0482",
                   firstName='Matthias', last_name='Probst')
        # as we have set an alias, we can also use "lastName":
        p = Person(id="https://orcid.org/0000-0001-8729-0482",
                   firstName='Matthias', lastName='Probst')

        json_ld_serialization = p.model_dump_jsonld()
        serialized_str = p.serialize(format="json-ld")
        expected = """{
  "@context": {
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "prov": "https://www.w3.org/ns/prov#",
    "foaf": "https://xmlns.com/foaf/0.1/",
    "m4i": "http://w3id.org/nfdi4ing/metadata4ing#"
  },
  "@id": "https://orcid.org/0000-0001-8729-0482",
  "@type": "prov:Person",
  "foaf:firstName": "Matthias",
  "foaf:lastName": "Probst"
}"""
        self.assertDictEqual(json.loads(json_ld_serialization), json.loads(expected))
        self.assertDictEqual(json.loads(serialized_str), json.loads(expected))

    def test_code2_on_readme(self):
        Event = build(
            namespace="https://schema.org/",
            namespace_prefix="schema",
            class_name="Event",
            properties=[Property(
                name="about",
                default=None,
                property_type=Union[Thing, List[Thing]]
            )]
        )
        conference = Event(label="my conference", about=[Thing(label='The thing it is about')])
        ttl = conference.serialize(format="ttl")
        expected = """@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .

[] a schema:Event ;
    rdfs:label "my conference" ;
    schema:about [ a owl:Thing ;
            rdfs:label "The thing it is about" ] .

"""
        self.assertEqual(ttl, expected)
