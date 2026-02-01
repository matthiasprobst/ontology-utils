import unittest

from ontolutils.ex import time


class TestTime(unittest.TestCase):

    def test_interval(self):
        interval = time.Interval(
            id="http://example.org/intervals/1",
            label="Test Interval",
            has_beginning=time.Instant(label="Start Instant", datetime="2024-01-01T00:00:00Z"),
            has_end=time.Instant(label="End Instant", datetime="2024-12-31T23:59:59Z"),
        )
        print(interval)

    def test_describing_simulation_time_interval(self):
        trs = time.TRS(
            id="http://example.org/trs/cfd",
            label="CFD Simulation pseudo-time (seconds since t=0s)"
        )

        simulation_interval = time.Interval(
            id="http://example.org/simulations/1/time_interval",
            label="Simulation Time Interval",
            has_beginning=time.Instant(
                label="Simulation Start",
                in_time_position=time.TimePosition(
                    has_trs=trs,
                    numeric_position=10.0 # 10s since t=0s
                )
            ),
            has_end=time.Instant(
                label="Simulation End",
                in_time_position=time.TimePosition(
                    has_trs=trs,
                    numeric_position=20.0 # 20s since t=0s
                )
            )
        )
        ttl = simulation_interval.serialize("ttl")
        self.assertEqual(ttl, """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix time: <http://www.w3.org/2006/time#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.org/simulations/1/time_interval> a time:Interval ;
    rdfs:label "Simulation Time Interval" ;
    time:hasBeginning [ a time:Instant ;
            rdfs:label "Simulation Start" ;
            time:inTimePosition [ a time:TimePosition ;
                    time:hasTRS <http://example.org/trs/cfd> ;
                    time:numericPosition 1e+01 ] ] ;
    time:hasEnd [ a time:Instant ;
            rdfs:label "Simulation End" ;
            time:inTimePosition [ a time:TimePosition ;
                    time:hasTRS <http://example.org/trs/cfd> ;
                    time:numericPosition 2e+01 ] ] .

<http://example.org/trs/cfd> a time:TRS ;
    rdfs:label "CFD Simulation pseudo-time (seconds since t=0s)" .

""")