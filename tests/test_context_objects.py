"""Valid JSON-LD context directives and term objects are not namespace strings."""
import json

from rdflib import Graph, RDF, URIRef

from ontolutils.ex.prov import Person


def test_structured_context_keeps_directives_and_resource_identity():
    person = Person(id='https://example.org/ada', firstName='Ada')
    context = {'@version': 1.1, '@vocab': 'https://example.org/',
               'ex': {'@id': 'https://example.org/', '@prefix': True},
               'unit': {'@id': 'https://example.org/unit', '@type': '@id'}}
    payload = person.model_dump_jsonld(context=context)
    graph = Graph().parse(data=payload, format='json-ld')
    assert (URIRef(person.id), RDF.type, URIRef('http://www.w3.org/ns/prov#Person')) in graph
    assert json.loads(payload)['@context']['@version'] == 1.1
    turtle = person.serialize('ttl', context=context)
    assert (URIRef(person.id), RDF.type, URIRef('http://www.w3.org/ns/prov#Person')) in Graph().parse(data=turtle, format='turtle')
