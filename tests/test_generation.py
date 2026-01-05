import logging
import pathlib
import unittest
from pprint import pprint

from ontolutils.generation import parser, writer

LOG_LEVEL = logging.DEBUG

__this_dir__ = pathlib.Path(__file__).parent


class TestGeneration(unittest.TestCase):

    def test_parse_dcat3(self):
        ontology_file = __this_dir__ / "data/dcat3.ttl"
        self.assertTrue(ontology_file.exists())

        parsed_ontology = parser.turtle_to_class_dicts(ontology_file)
        pprint(parsed_ontology[0])
        for p in parsed_ontology:
            if p["label"] == "Catalog":
                self.assertEqual(p["class"], "http://www.w3.org/ns/dcat#Catalog")
                self.assertEqual(p["class"], "http://www.w3.org/ns/dcat#Catalog")
                self.assertEqual(p["superclasses"], ["http://www.w3.org/ns/dcat#Dataset"])
                found_dataset = False
                for prop in p["properties"]:
                    if prop["property"] == "http://www.w3.org/ns/dcat#dataset" and prop[
                        "range"] == "http://www.w3.org/ns/dcat#Dataset":
                        found_dataset = True
                self.assertTrue(found_dataset)

    def test_parsed_dict_to_string(self):
        data = {'class': 'http://www.w3.org/ns/dcat#Catalog',
                'label': 'Catalog',
                'properties': [{'implied': None,
                                'kind': 'object',
                                'property': 'http://www.w3.org/ns/dcat#catalog',
                                'range': 'http://www.w3.org/ns/dcat#Catalog',
                                'restriction': None},
                               {'implied': None,
                                'kind': 'object',
                                'property': 'http://www.w3.org/ns/dcat#dataset',
                                'range': 'http://www.w3.org/ns/dcat#Dataset',
                                'restriction': None},
                               {'implied': None,
                                'kind': 'object',
                                'property': 'http://www.w3.org/ns/dcat#record',
                                'range': 'http://www.w3.org/ns/dcat#CatalogRecord',
                                'restriction': None},
                               {'implied': None,
                                'kind': 'object',
                                'property': 'http://www.w3.org/ns/dcat#resource',
                                'range': 'http://www.w3.org/ns/dcat#Resource',
                                'restriction': None},
                               {'implied': None,
                                'kind': 'object',
                                'property': 'http://www.w3.org/ns/dcat#service',
                                'range': 'http://www.w3.org/ns/dcat#DataService',
                                'restriction': None},
                               {'implied': None,
                                'kind': 'object',
                                'property': 'http://www.w3.org/ns/dcat#themeTaxonomy',
                                'range': 'http://www.w3.org/2000/01/rdf-schema#Resource',
                                'restriction': None}],
                'subclasses': [],
                'superclasses': ['http://www.w3.org/ns/dcat#Dataset']}
        out = writer.to_string(
            data,
            prefix_map={
                "http://www.w3.org/ns/dcat#": "dcat",
                "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
            },
            namespace_value_for_prefix={
                "dcat": "http://www.w3.org/ns/dcat#",
            }, )
        print(out)
