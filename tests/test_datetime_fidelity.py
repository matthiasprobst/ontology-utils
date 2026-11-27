"""A midnight datetime must never be silently reduced to a calendar date."""
from datetime import datetime, timedelta, timezone
from typing import List

import pytest
from rdflib import Graph, URIRef, XSD

from ontolutils import Thing, namespaces, urirefs


@namespaces(ex='https://example.org/')
@urirefs(Event='ex:Event', occurred='ex:occurred', observations='ex:observations')
class Event(Thing):
    occurred: datetime
    observations: List[datetime]


@pytest.mark.parametrize('value', [datetime(2026, 1, 1),
    datetime(2026, 1, 1, tzinfo=timezone.utc),
    datetime(2026, 1, 1, microsecond=123456, tzinfo=timezone.utc),
    datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=5, minutes=30))),
    datetime(2026, 1, 1, 12, 34, 56, 123456, tzinfo=timezone(timedelta(hours=-4)))])
def test_datetime_precision_and_offset_survive_rdf_round_trip(value):
    original = Event(id='https://example.org/event', occurred=value, observations=[value])
    for format in ['json-ld', 'ttl', 'xml']:
        graph = Graph().parse(data=original.serialize(format), format=format)
        for field in ['occurred', 'observations']:
            literal = next(graph.objects(URIRef(original.id), URIRef(Event.iri(field))))
            assert literal.datatype == XSD.dateTime
            assert literal.toPython() == value
            assert literal.toPython().utcoffset() == value.utcoffset()
            assert literal.toPython().microsecond == value.microsecond
        restored = Event.from_graph(graph, limit=1)
        assert restored.occurred == value
        assert restored.observations == [value]
        assert restored.occurred.utcoffset() == value.utcoffset()


def test_nested_datetime_preserves_midnight_and_microseconds():
    value = datetime(2026, 1, 1, microsecond=1, tzinfo=timezone.utc)
    event = Event(id='https://example.org/event', occurred=value, observations=[value])
    container = Thing(about=event)
    graph = Graph().parse(data=container.serialize('ttl'), format='ttl')
    literal = next(graph.objects(URIRef(event.id), URIRef(Event.iri('occurred'))))
    assert literal.datatype == XSD.dateTime
    assert literal.toPython() == value
