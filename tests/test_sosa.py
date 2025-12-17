import unittest

from ontolutils import serialize
from ontolutils.ex.m4i import Tool
from ontolutils.ex.qudt import Unit
from ontolutils.ex.sosa import ObservableProperty, Sensor, Platform
from ontolutils.ex.ssn import Accuracy, SystemCapability, MeasurementRange


class TestSosa(unittest.TestCase):

    def test_obervable_property(self):
        oprop = ObservableProperty(
            id="http://example.org/observable_property/1",
            isObservedBy="http://example.org/sensor/1"
        )
        self.assertEqual(oprop.serialize("ttl"),
                         """@prefix sosa: <http://www.w3.org/ns/sosa/> .

<http://example.org/observable_property/1> a sosa:ObservableProperty ;
    sosa:isObservedBy <http://example.org/sensor/1> .

""")

    def test_platform(self):
        oprop = ObservableProperty(
            id="http://example.org/observable_property/1",
            isObservedBy="http://example.org/sensor/1"
        )
        sensor = Sensor(
            id="http://example.org/sensor/1",
            observes=oprop,
            isHostedBy="http://example.org/platform/1"
        )
        platform = Platform(
            id="http://example.org/platform/1",
            hosts=sensor
        )
        print(platform.serialize("ttl"))
        self.assertEqual(platform.serialize("ttl"), """@prefix sosa: <http://www.w3.org/ns/sosa/> .

<http://example.org/observable_property/1> a sosa:ObservableProperty ;
    sosa:isObservedBy <http://example.org/sensor/1> .

<http://example.org/platform/1> a sosa:Platform ;
    sosa:hosts <http://example.org/sensor/1> .

<http://example.org/sensor/1> a sosa:Sensor ;
    sosa:isHostedBy <http://example.org/platform/1> ;
    sosa:observes <http://example.org/observable_property/1> .

""")

    def test_tool_and_sensor(self):
        oprop = ObservableProperty(
            id="http://example.org/observable_property/1",
            isObservedBy="http://example.org/sensor/1"
        )
        sensor = Sensor(
            id="http://example.org/tool/1",
            observes=oprop
        )
        tool = Tool(
            id="http://example.org/tool/1"
        )
        ttl = serialize(
            [tool, sensor], "ttl"
        )
        self.assertEqual(ttl, """@prefix m4i: <http://w3id.org/nfdi4ing/metadata4ing#> .
@prefix sosa: <http://www.w3.org/ns/sosa/> .

<http://example.org/tool/1> a m4i:Tool,
        sosa:Sensor ;
    sosa:observes <http://example.org/observable_property/1> .

<http://example.org/observable_property/1> a sosa:ObservableProperty ;
    sosa:isObservedBy <http://example.org/sensor/1> .

""")

    def test_sensor_with_accuracy(self):
        oprop = ObservableProperty(
            id="http://example.org/observable_property/1",
        )
        measurement_range1 = MeasurementRange(
            id="http://example.org/measurement_range/1",
            min_value="0",
            max_value="250",
            unit_code=Unit(
                id="http://qudt.org/vocab/unit/PA"
            )
        )
        u_pa = Unit(
            id="http://qudt.org/vocab/unit/PA"
        )
        measurement_range2 = MeasurementRange(
            id="http://example.org/measurement_range/2",
            min_value="0",
            max_value="500",
            unit_code=u_pa
        )
        accuracy_1 = Accuracy(
            id="http://example.org/accuracy/1",
            value=0.01 * 250,
            unit_code=u_pa,
            comment="Max error bound (±1%FS) for range 0–250 Pa (FS=250 Pa).@en"
        )
        accuracy_2 = Accuracy(
            id="http://example.org/accuracy/2",
            value=0.01 * 500,
            unit_code=u_pa,
            comment="Max error bound (±1%FS) for range 0–500 Pa (FS=500 Pa).@en"
        )
        capability_1 = SystemCapability(
            id="http://example.org/system_capability/1",
            hasSystemProperty=[accuracy_1, measurement_range1],
            forProperty=oprop
        )
        capability_2 = SystemCapability(
            id="http://example.org/system_capability/2",
            hasSystemProperty=[accuracy_2, measurement_range2],
            forProperty=oprop
        )
        sensor = Sensor(
            id="http://example.org/tool/KalinskyDS2-1",
            observes=oprop,
            hasSystemCapability=[capability_1, capability_2],
            label="Kalinsky Sensor TYPE DS 1@en"
        )
        ttl = sensor.serialize("ttl")
        self.assertEqual(ttl, """@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema1: <http://schema.org/> .
@prefix sosa: <http://www.w3.org/ns/sosa/> .
@prefix ssn: <http://www.w3.org/ns/ssn/> .
@prefix ssn_system: <http://www.w3.org/ns/ssn/systems/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.org/tool/KalinskyDS2-1> a sosa:Sensor ;
    rdfs:label "Kalinsky Sensor TYPE DS 1"@en ;
    sosa:observes <http://example.org/observable_property/1> ;
    ssn_system:hasSystemCapability <http://example.org/system_capability/1>,
        <http://example.org/system_capability/2> .

<http://example.org/accuracy/1> a ssn_system:Accuracy ;
    schema1:unitCode <http://qudt.org/vocab/unit/PA> ;
    schema1:value 2.5e+00 ;
    rdfs:comment "Max error bound (±1%FS) for range 0–250 Pa (FS=250 Pa)."@en .

<http://example.org/accuracy/2> a ssn_system:Accuracy ;
    schema1:unitCode <http://qudt.org/vocab/unit/PA> ;
    schema1:value 5e+00 ;
    rdfs:comment "Max error bound (±1%FS) for range 0–500 Pa (FS=500 Pa)."@en .

<http://example.org/measurement_range/1> a ssn_system:MeasurementRange ;
    schema1:maxValue 2.5e+02 ;
    schema1:minValue 0e+00 ;
    schema1:unitCode <http://qudt.org/vocab/unit/PA> .

<http://example.org/measurement_range/2> a ssn_system:MeasurementRange ;
    schema1:maxValue 5e+02 ;
    schema1:minValue 0e+00 ;
    schema1:unitCode <http://qudt.org/vocab/unit/PA> .

<http://example.org/system_capability/1> a ssn_system:SystemCapability ;
    ssn:forProperty <http://example.org/observable_property/1> ;
    ssn_system:hasSystemProperty <http://example.org/accuracy/1>,
        <http://example.org/measurement_range/1> .

<http://example.org/system_capability/2> a ssn_system:SystemCapability ;
    ssn:forProperty <http://example.org/observable_property/1> ;
    ssn_system:hasSystemProperty <http://example.org/accuracy/2>,
        <http://example.org/measurement_range/2> .

<http://example.org/observable_property/1> a sosa:ObservableProperty .

<http://qudt.org/vocab/unit/PA> a qudt:Unit .

""")