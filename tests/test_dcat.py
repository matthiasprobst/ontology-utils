import datetime
import logging
import pathlib
import sys
import unittest
from datetime import timezone

import rdflib

import utils
from ontolutils.ex import dcat, prov, foaf
from ontolutils.ex.dcat import Dataset
from ontolutils.ex.prov import Attribution
from ontolutils.ex.spdx import Checksum
from ontolutils.namespacelib.spdx import SPDX

logger = logging.getLogger('ontolutils')
__this_dir__ = pathlib.Path(__file__).parent

TESTING_VERSIONS = (9, 14)


def get_python_version():
    """Get the current Python version as a tuple."""
    return sys.version_info.major, sys.version_info.minor, sys.version_info.micro


class TestDcat(utils.ClassTest):

    def test_Resource(self):
        resource1 = dcat.Resource(
            id='https://example.com/resource',
            title='Resource title',
            description='Resource description',
            creator=prov.Person(first_name='John', lastName='Doe'),
            version='1.0',
            issued="2023-01-01T00:00:00Z",
            identifier='https://example.com/resource'
        )
        self.assertEqual(resource1.id, 'https://example.com/resource')
        self.assertEqual(resource1.title, 'Resource title')
        self.assertEqual(resource1.issued, datetime.datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc))
        self.assertEqual(resource1.description, 'Resource description')
        self.assertIsInstance(resource1.creator, prov.Person)
        self.assertEqual(resource1.creator.firstName, 'John')
        self.assertEqual(resource1.creator.lastName, 'Doe')
        self.assertEqual(resource1.version, '1.0')
        self.assertEqual(str(resource1.identifier), 'https://example.com/resource')
        resource1.contributor = foaf.Organization(name='Example Org')
        self.assertIsInstance(resource1.contributor, foaf.Organization)
        print(resource1.serialize("ttl"))
        self.assertEqual(resource1.serialize("ttl"), """@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://example.com/resource> a dcat:Resource ;
    dcterms:contributor [ a foaf:Organization ;
            foaf:name "Example Org" ] ;
    dcterms:creator [ a prov:Person ;
            foaf:firstName "John" ;
            foaf:lastName "Doe" ] ;
    dcterms:description "Resource description" ;
    dcterms:identifier <https://example.com/resource> ;
    dcterms:issued "2023-01-01"^^xsd:date ;
    dcterms:title "Resource title" ;
    dcat:version "1.0" .

""")

    def test_License(self):
        license1 = "https://creativecommons.org/licenses/by/4.0/"
        resource = dcat.Resource(
            title='Resource title',
            description='Resource description',
            license="cc-by-4.0"
        )
        self.assertEqual(str(resource.license), license1)
        self.assertEqual("""@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

[] a dcat:Resource ;
    dcterms:description "Resource description" ;
    dcterms:license <https://creativecommons.org/licenses/by/4.0/> ;
    dcterms:title "Resource title" .

""",
                         resource.serialize("ttl"))
        dist = dcat.Distribution(
            title='Distribution title',
            description='Distribution description',
            license=license1,
            checksum=Checksum(
                algorithm='SHA256',
                value='d2d2d2d2d2d2d2d2d2d2'
            )
        )
        self.assertEqual(str(dist.license), license1)
        self.assertEqual(dist.checksum.algorithm, str(SPDX.checksumAlgorithm_sha256))

        dataset = dcat.Dataset(
            title='Distribution title',
            description='Distribution description',
            license=license1,
            distribution=dist
        )
        self.assertEqual(str(dataset.license), license1)
        self.assertEqual(str(dataset.distribution.license), license1)
        print(dataset.serialize("ttl"))
        print(dataset.model_dump_jsonld())

        multi_lic = dcat.Resource(
            title='Resource title',
            description='Resource description',
            license=[license1, "https://opensource.org/licenses/MIT"]
        )
        self.assertEqual(multi_lic.license, [license1, "https://opensource.org/licenses/MIT"])

    def test_has_part(self):
        r1 = dcat.Resource(
            id='https://example.com/resource1',
            title='Resource 1',
            description='Resource 1 description',
            identifier='https://example.com/resource1'
        )
        r2 = dcat.Resource(
            id='https://example.com/resource2',
            title='Resource 2',
            description='Resource 2 description',
            identifier='https://example.com/resource2',
            has_part=r1
        )
        self.assertEqual(r2.hasPart.id, r1.id)

        r3 = dcat.Resource(
            id='https://example.com/resource3',
            title='Resource 3',
            description='Resource 3 description',
            identifier='https://example.com/resource3',
            has_part=[r1, r2]
        )
        self.assertEqual(len(r3.hasPart), 2)
        self.assertEqual(r3.hasPart[0].id, r1.id)
        self.assertEqual(r3.hasPart[1].id, r2.id)
        self.assertEqual("""@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<https://example.com/resource3> a dcat:Resource ;
    dcterms:description "Resource 3 description" ;
    dcterms:hasPart <https://example.com/resource1>,
        <https://example.com/resource2> ;
    dcterms:identifier <https://example.com/resource3> ;
    dcterms:title "Resource 3" .

<https://example.com/resource2> a dcat:Resource ;
    dcterms:description "Resource 2 description" ;
    dcterms:hasPart <https://example.com/resource1> ;
    dcterms:identifier <https://example.com/resource2> ;
    dcterms:title "Resource 2" .

<https://example.com/resource1> a dcat:Resource ;
    dcterms:description "Resource 1 description" ;
    dcterms:identifier <https://example.com/resource1> ;
    dcterms:title "Resource 1" .

""", r3.serialize("ttl"))

    def test_basic_distribution(self):
        dist = dcat.Distribution(
            title='Distribution title',
            description='Distribution description',
            media_type='application/x-hdf'
        )
        self.assertEqual(dist.mediaType, 'https://www.iana.org/assignments/media-types/application/x-hdf')
        dist = dcat.Distribution(
            title='Distribution title',
            description='Distribution description',
            media_type='https://www.iana.org/assignments/media-types/application/json'
        )
        self.assertEqual(dist.mediaType, 'https://www.iana.org/assignments/media-types/application/json')
        dist = dcat.Distribution(
            title='Distribution title',
            description='Distribution description',
            media_type='text/csv'
        )
        self.assertEqual(dist.mediaType, 'https://www.iana.org/assignments/media-types/text/csv')

        dist = dcat.Distribution(
            title='Distribution title',
            mediaType="hdf"
        )
        self.assertEqual(dist.mediaType, 'https://www.iana.org/assignments/media-types/application/x-hdf')

    @unittest.skipUnless(get_python_version()[1] in TESTING_VERSIONS,
                         reason="Only testing on min and max python version")
    def test_Distribution(self):
        distribution_none_downloadURL = dcat.Distribution(
            id='_:b2',
            title='Distribution title',
            description='Distribution description'
        )
        self.assertEqual(distribution_none_downloadURL.id, '_:b2')
        with self.assertRaises(ValueError):
            distribution_none_downloadURL.download()

        distribution_wrongfile = dcat.Distribution(
            title='Distribution title',
            description='Distribution description',
            downloadURL=(__this_dir__ / "does-not-exist.txt").resolve().absolute()
        )
        with self.assertRaises(FileNotFoundError):
            distribution_wrongfile.download()

        distribution1 = dcat.Distribution(
            id='https://example.com/distribution',
            title='Distribution title',
            description='Distribution description',
            creator=prov.Person(first_name='John', lastName='Doe'),
            version='1.0',
            identifier='https://example.com/distribution',
            accessURL='https://example.com/distribution',
            downloadURL='https://example.com/distribution/download'
        )
        self.assertEqual(distribution1.id, 'https://example.com/distribution')
        self.assertEqual(distribution1.title, 'Distribution title')
        self.assertEqual(distribution1.description, 'Distribution description')
        self.assertIsInstance(distribution1.creator, prov.Person)
        self.assertEqual(distribution1.creator.firstName, 'John')
        self.assertEqual(distribution1.creator.lastName, 'Doe')
        self.assertEqual(distribution1.version, '1.0')
        self.assertEqual(str(distribution1.identifier), 'https://example.com/distribution')
        self.assertEqual(str(distribution1.accessURL), 'https://example.com/distribution')
        self.assertEqual(str(distribution1.downloadURL), 'https://example.com/distribution/download')

        pathlib.Path("piv_dataset.jsonld").unlink(missing_ok=True)
        piv_dist = dcat.Distribution(
            downloadURL=self.test_jsonld_filename
        )
        filename = piv_dist.download(timeout=10)
        self.assertEqual(filename.name, 'piv_dataset.jsonld')
        self.assertIsInstance(filename, pathlib.Path)
        self.assertTrue(filename.exists())

        local_dist = dcat.Distribution(
            downloadURL=filename
        )
        local_filename = local_dist.download(timeout=60)
        self.assertTrue(local_filename.exists())
        self.assertEqual(local_filename.name, 'piv_dataset.jsonld')
        self.assertIsInstance(local_filename, pathlib.Path)

        filename.unlink(missing_ok=True)

    def test_Dataset(self):
        person = prov.Person(id="https://example.of/123", first_name='John', lastName='Doe')
        dataset1 = dcat.Dataset(
            id='https://example.com/dataset',
            title='Dataset title',
            description='Dataset description',
            creator=person,
            version='1.0',
            identifier='https://example.com/dataset',
            distribution=[
                dcat.Distribution(
                    id='https://example.com/distribution',
                    title='Distribution title',
                    description='Distribution description',
                    identifier='https://example.com/distribution',
                    accessURL='https://example.com/distribution',
                    downloadURL='https://example.com/distribution/download'
                )
            ],
            qualifiedAttribution=Attribution(agent=person)
        )
        print(dataset1.serialize("ttl"))
        self.assertEqual(dataset1.qualifiedAttribution.agent.id, person.id)
        self.assertEqual(dataset1.qualifiedAttribution.agent.firstName, "John")
        self.assertEqual(dataset1.id, 'https://example.com/dataset')
        self.assertEqual(dataset1.identifier, 'https://example.com/dataset')
        self.assertEqual(dataset1.title, 'Dataset title')
        self.assertEqual(dataset1.description, 'Dataset description')
        self.assertIsInstance(dataset1.creator, prov.Person)
        self.assertEqual(dataset1.creator.firstName, 'John')
        self.assertEqual(dataset1.creator.lastName, 'Doe')
        self.assertEqual(dataset1.version, '1.0')
        self.assertEqual(str(dataset1.identifier), 'https://example.com/dataset')
        self.assertIsInstance(dataset1.distribution[0], dcat.Distribution)
        self.assertEqual(dataset1.distribution[0].title, 'Distribution title')
        self.assertEqual(dataset1.distribution[0].description, 'Distribution description')
        self.assertEqual(str(dataset1.distribution[0].id), 'https://example.com/distribution')
        self.assertEqual(str(dataset1.distribution[0].identifier), 'https://example.com/distribution')
        self.assertEqual(str(dataset1.distribution[0].accessURL), 'https://example.com/distribution')
        self.assertEqual(str(dataset1.distribution[0].downloadURL), 'https://example.com/distribution/download')

        ds = dcat.Dataset(
            id='https://example.com/dataset',
            title='Dataset title',
            description='Dataset description',
            creator=person.id,
            version='1.0',
            identifier='https://example.com/dataset',
            distribution=[
                dcat.Distribution(
                    id='https://example.com/distribution',
                    title='Distribution title',
                    description='Distribution description',
                    identifier='https://example.com/distribution',
                    accessURL='https://example.com/distribution',
                    downloadURL='https://example.com/distribution/download'
                )
            ]
        )
        ttl = ds.serialize("ttl")
        self.assertEqual(ttl, """@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<https://example.com/dataset> a dcat:Dataset ;
    dcterms:creator <https://example.of/123> ;
    dcterms:description "Dataset description" ;
    dcterms:identifier <https://example.com/dataset> ;
    dcterms:title "Dataset title" ;
    dcat:distribution <https://example.com/distribution> ;
    dcat:version "1.0" .

<https://example.com/distribution> a dcat:Distribution ;
    dcterms:description "Distribution description" ;
    dcterms:identifier <https://example.com/distribution> ;
    dcterms:title "Distribution title" ;
    dcat:accessURL <https://example.com/distribution> ;
    dcat:downloadURL <https://example.com/distribution/download> .

""")

    def test_Dataset_with_foaf(self):
        person = foaf.Person(openid="http://example.com/people/johndoe",

                             first_name='John', family_name='Doe')
        self.assertEqual(person.id, 'http://example.com/people/johndoe')
        dataset1 = dcat.Dataset(
            id='https://example.com/dataset',
            title='Dataset title',
            description='Dataset description',
            creator=person,
            version='1.0',
            identifier='https://example.com/dataset',
            distribution=[
                dcat.Distribution(
                    id='https://example.com/distribution',
                    title='Distribution title',
                    description='Distribution description',
                    identifier='https://example.com/distribution',
                    accessURL='https://example.com/distribution',
                    downloadURL='https://example.com/distribution/download'
                )
            ]
        )
        self.assertEqual(dataset1.id, 'https://example.com/dataset')
        self.assertEqual(dataset1.identifier, 'https://example.com/dataset')
        self.assertEqual(dataset1.title, 'Dataset title')
        self.assertEqual(dataset1.description, 'Dataset description')
        self.assertIsInstance(dataset1.creator, foaf.Person)
        self.assertEqual(dataset1.creator.firstName, 'John')
        self.assertEqual(dataset1.creator.familyName, 'Doe')
        self.assertEqual(dataset1.version, '1.0')
        self.assertEqual(str(dataset1.identifier), 'https://example.com/dataset')
        self.assertIsInstance(dataset1.distribution[0], dcat.Distribution)
        self.assertEqual(dataset1.distribution[0].title, 'Distribution title')
        self.assertEqual(dataset1.distribution[0].description, 'Distribution description')
        self.assertEqual(str(dataset1.distribution[0].id), 'https://example.com/distribution')
        self.assertEqual(str(dataset1.distribution[0].identifier), 'https://example.com/distribution')
        self.assertEqual(str(dataset1.distribution[0].accessURL), 'https://example.com/distribution')
        self.assertEqual(str(dataset1.distribution[0].downloadURL), 'https://example.com/distribution/download')

        dataset2 = dcat.Dataset(
            id='https://example.com/dataset',
            title='Dataset title',
            description='Dataset description',
            creator=person.id,
            version='1.0',
            identifier='https://example.com/dataset',
            distribution=[
                dcat.Distribution(
                    id='https://example.com/distribution',
                    title='Distribution title',
                    description='Distribution description',
                    identifier='https://example.com/distribution',
                    accessURL='https://example.com/distribution',
                    downloadURL='https://example.com/distribution/download'
                )
            ]
        )
        self.assertEqual(str(dataset2.creator), str(person.id))

    def test_was_generated_by(self):
        from ontolutils.ex.m4i import ProcessingStep
        processing_step = ProcessingStep(
            id='https://example.com/processingstep/1',
            used='http://example.com/resource/1',
            start_time="2023-01-01T12:00:00Z",
            startedAtTime="2023-01-01T12:00:00Z",
        )
        self.assertEqual(processing_step.serialize("ttl"), """@prefix m4i: <http://w3id.org/nfdi4ing/metadata4ing#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix schema: <https://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://example.com/processingstep/1> a m4i:ProcessingStep ;
    prov:startedAtTime "2023-01-01T12:00:00+00:00"^^xsd:dateTime ;
    prov:used <http://example.com/resource/1> ;
    schema:startTime "2023-01-01T12:00:00+00:00"^^xsd:dateTime .

""")
        dist = dcat.Distribution(
            id='https://example.com/distribution/1',
            label='Distribution 1',
            creator='https://example.com/creator/1',
            byteSize=123456
        )
        ds = dcat.Dataset(
            id='https://example.com/dataset/1',
            title='Dataset 1',
            distribution=dist,
            was_generated_by=processing_step,
        )
        self.assertEqual(ds.serialize(format="ttl"), """@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix m4i: <http://w3id.org/nfdi4ing/metadata4ing#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://example.com/dataset/1> a dcat:Dataset ;
    dcterms:title "Dataset 1" ;
    dcat:distribution <https://example.com/distribution/1> ;
    prov:wasGeneratedBy <https://example.com/processingstep/1> .

<https://example.com/distribution/1> a dcat:Distribution ;
    rdfs:label "Distribution 1" ;
    dcterms:creator <https://example.com/creator/1> ;
    dcat:byteSize 123456 .

<https://example.com/processingstep/1> a m4i:ProcessingStep ;
    prov:startedAtTime "2023-01-01T12:00:00+00:00"^^xsd:dateTime ;
    prov:used <http://example.com/resource/1> ;
    schema:startTime "2023-01-01T12:00:00+00:00"^^xsd:dateTime .

""")

    def test_dcat_DataService(self):
        data_service = dcat.DataService(
            id="http://local.org/sqlite3",
            title="sqlite3 Database",
            endpointURL="file:///path/to/endpoint",
            servesDataset=dcat.Dataset(
                title="Table Title",
                description="An SQL Table with the name 'Table Title'",
                distribution=dcat.Distribution(
                    id="http://local.org/sqlite3/12345",
                    identifier="12345",
                    mediaType="application/vnd.sqlite3",
                )
            )
        )
        self.assertEqual(data_service.id, "http://local.org/sqlite3")
        self.assertIsInstance(data_service, dcat.DataService)
        self.assertEqual(data_service.servesDataset.distribution.identifier, "12345")
        self.assertEqual(data_service.serialize("ttl"), """@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<http://local.org/sqlite3> a dcat:DataService ;
    dcterms:title "sqlite3 Database" ;
    dcat:endpointURL "file:///path/to/endpoint" ;
    dcat:servesDataset [ a dcat:Dataset ;
            dcterms:description "An SQL Table with the name 'Table Title'" ;
            dcterms:title "Table Title" ;
            dcat:distribution <http://local.org/sqlite3/12345> ] .

<http://local.org/sqlite3/12345> a dcat:Distribution ;
    dcterms:identifier "12345" ;
    dcat:mediaType <https://www.iana.org/assignments/media-types/application/vnd.sqlite3> .

""")

    def test_catalog(self):
        catalog = dcat.Catalog(
            id="http://example.com/catalog/1",
            title="Example Catalog",
            description="An example DCAT catalog",
            dataset=[
                dcat.Dataset(
                    id="http://example.com/dataset/1",
                    title="Dataset 1",
                    description="The first dataset",
                    identifier="ds1"
                ),
                dcat.Dataset(
                    id="http://example.com/dataset/2",
                    title="Dataset 2",
                    description="The second dataset",
                    identifier="ds2"
                )
            ]
        )
        self.assertEqual(catalog.id, "http://example.com/catalog/1")
        self.assertEqual(len(catalog.dataset), 2)
        self.assertEqual(catalog.dataset[0].identifier, "ds1")
        self.assertEqual(catalog.dataset[1].identifier, "ds2")
        self.assertEqual("""@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<http://example.com/catalog/1> a dcat:Catalog ;
    dcterms:description "An example DCAT catalog" ;
    dcterms:title "Example Catalog" ;
    dcat:dataset <http://example.com/dataset/1>,
        <http://example.com/dataset/2> .

<http://example.com/dataset/1> a dcat:Dataset ;
    dcterms:description "The first dataset" ;
    dcterms:identifier "ds1" ;
    dcterms:title "Dataset 1" .

<http://example.com/dataset/2> a dcat:Dataset ;
    dcterms:description "The second dataset" ;
    dcterms:identifier "ds2" ;
    dcterms:title "Dataset 2" .

""", catalog.serialize("ttl"))

    def test_query_dataset_based_on_constructing_query_from_itself(self):
        q = Dataset.create_query()
        print(q)
        g = rdflib.Graph()
        g.parse(__this_dir__ / "data/catalog.ttl")
        res = g.query(q)
        for row in res:
            print(sparql_result_to_dict(row))
            # pprint({k: row[v] for k, v in row.labels.items() if row[v] is not None})
            # print("\n---\n")


def sparql_result_to_dict(bindings, exclude_none=True):
    """Convert a SPARQL query result row to a dictionary."""
    if exclude_none:
        return {k: bindings[v] for k, v in bindings.labels.items() if bindings[v] is not None}
    return {k: bindings[v] for k, v in bindings.labels.items() if bindings[v]}
