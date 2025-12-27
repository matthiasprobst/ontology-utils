import unittest

import pydantic
import rdflib
from pydantic import HttpUrl, ValidationError

from ontolutils import Thing, urirefs, namespaces
from ontolutils import set_logging_level
from ontolutils import typing
from ontolutils.typing import OptionalResourceTypeOrListOf

set_logging_level('WARNING')


class TestTypeing(unittest.TestCase):

    def test_blank_node(self):
        class MyModel(pydantic.BaseModel):
            blank_node: typing.BlankNodeType

        with self.assertRaises(pydantic.ValidationError):
            MyModel(blank_node='b1')

        with self.assertRaises(pydantic.ValidationError):
            MyModel(blank_node='_b1')

        MyModel(blank_node='_:b1')

    def test_resource_type(self):
        @namespaces(dcterms="http://purl.org/dc/terms/",
                    dcat="http://www.w3.org/ns/dcat#")
        @urirefs(Dataset='dcat:Dataset',
                 hasVersion='dcterms:hasVersion')
        class Dataset(Thing):
            """
            A dataset class.
            """
            hasVersion: OptionalResourceTypeOrListOf

        with self.assertRaises(ValidationError):
            Dataset(
                label="Test ds@en",
                hasVersion="v1.0"
            )

        ds = Dataset(
            label="Test ds@en",
            hasVersion="http://example.org/resource/version/v1.0"
        )
        ttl = ds.serialize("ttl")
        self.assertEqual(ttl, """@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

[] a dcat:Dataset ;
    rdfs:label "Test ds"@en ;
    dcterms:hasVersion <http://example.org/resource/version/v1.0> .

""")

        ds = Dataset(
            label="Test ds@en",
            hasVersion=["http://example.org/resource/version/v1.0",
                        "http://example.org/resource/version/v2.0"]
        )
        ttl = ds.serialize("ttl")
        self.assertEqual(ttl, """@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

[] a dcat:Dataset ;
    rdfs:label "Test ds"@en ;
    dcterms:hasVersion <http://example.org/resource/version/v1.0>,
        <http://example.org/resource/version/v2.0> .

""")

        version = Thing(
            id="http://example.org/resource/version/v1.0",
            label="v1.0"
        )

        ds = Dataset(
            label="Test ds@en",
            hasVersion=version
        )
        ttl = ds.serialize("ttl")
        self.assertEqual(ttl, """@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/resource/version/v1.0> a owl:Thing ;
    rdfs:label "v1.0" .

[] a dcat:Dataset ;
    rdfs:label "Test ds"@en ;
    dcterms:hasVersion <http://example.org/resource/version/v1.0> .

""")

        ds = Dataset(
            label="Test ds@en",
            hasVersion=rdflib.URIRef("http://example.org/resource/version/v1.0")
        )
        self.assertEqual("http://example.org/resource/version/v1.0", ds.hasVersion)
        ds = Dataset(
            label="Test ds@en",
            hasVersion=HttpUrl("http://example.org/resource/version/v1.0")
        )
        self.assertEqual("http://example.org/resource/version/v1.0", ds.hasVersion)
