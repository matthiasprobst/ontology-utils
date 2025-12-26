import datetime
import pathlib
import unittest

from ontolutils import cache
from ontolutils.ex import prov

__this_dir__ = pathlib.Path(__file__).parent
CACHE_DIR = cache.get_cache_dir()


class TestPROV(unittest.TestCase):

    def test_agent_with_extra_fields(self):
        agent = prov.Agent(
            id='_:b1',
            name='Agent name',
            mbox='a@email.com')
        self.assertEqual(agent.id, '_:b1')

        agent = prov.Agent(
            id='_:b1',
            name='Agent name')
        self.assertEqual(agent.id, '_:b1')

    def test_activity_and_entity(self):
        e1 = prov.Entity(
            id='http://example.org/entity/1',
            label='Entity 1'
        )
        e2 = prov.Entity(
            id='http://example.org/entity/2',
            label='Entity 2',
            was_derived_from=e1
        )
        a = prov.Activity(
            id='http://example.org/activity/1',
            used=e2,
            generated=e1,
            startedAtTime=datetime.datetime.fromisoformat("2025-12-22T08:47:37.007873")
        )
        self.assertEqual("""@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.org/activity/1> a prov:Activity ;
    prov:generated <http://example.org/entity/1> ;
    prov:startedAtTime "2025-12-22T08:47:37.007873"^^xsd:dateTime ;
    prov:used <http://example.org/entity/2> .

<http://example.org/entity/2> a prov:Entity ;
    rdfs:label "Entity 2" ;
    prov:wasDerivedFrom <http://example.org/entity/1> .

<http://example.org/entity/1> a prov:Entity ;
    rdfs:label "Entity 1" .

""",
                         a.serialize("ttl"))

    def test_person_from_jsonld(self):
        person = prov.Person.from_jsonld(__this_dir__ / "data/prov_person.jsonld")
        self.assertEqual(1, len(person))
        self.assertEqual(person[0].mbox, "john.doe@mail.de")
        self.assertEqual(person[0].orcidId, "https://orcid.org/1234-1234-1234-1234")