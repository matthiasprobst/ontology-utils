import logging
import unittest
from typing import Union

from pydantic import Field, HttpUrl

from ontolutils import Thing, urirefs, namespaces, build

LOG_LEVEL = logging.DEBUG


class TestSchema(unittest.TestCase):

    def testSchemaHTTP(self):
        @namespaces(schema="https://schema.org/")
        @urirefs(SoftwareSourceCode='schema:SoftwareSourceCode',
                 code_repository='schema:codeRepository',
                 application_category='schema:applicationCategory')
        class SoftwareSourceCode(Thing):
            """Pydantic Model for https://schema.org/SoftwareSourceCode"""
            code_repository: Union[HttpUrl, str] = Field(default=None, alias="codeRepository")
            application_category: Union[str, HttpUrl] = Field(default=None, alias="applicationCategory")

        thing = SoftwareSourceCode.from_jsonld(data={
            "@id": "_:N123",
            "@type": "http://schema.org/SoftwareSourceCode",  # note, it is http instead of https!
            "codeRepository": "https://example.com/code",
            "applicationCategory": "https://example.com/category"
        })
        print(thing[0].model_dump_jsonld(indent=2))

    def test_event(self):
        # Event is not defined in the package
        from typing import List
        from ontolutils.classes.thing import Property
        event = build(
            namespace="https://schema.org/",
            namespace_prefix="schema",
            class_name="Event",
            properties=[Property(
                name="about",
                alias="about",
                default=None,
                property_type=Union[Thing, List[Thing]]
            )]
        )
        self.assertIsInstance(
            event(), Thing
        )
        conference = event(
            about=[Thing(label="my conference")]
        )
        serialized = conference.serialize("ttl")
        expected_serialization = """@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .

[] a schema:Event ;
    schema:about [ a owl:Thing ;
            rdfs:label "my conference" ] .

"""
        self.assertEqual(serialized, expected_serialization)
