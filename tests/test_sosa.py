import unittest

import rdflib

from ontolutils import serialize, Thing
from ontolutils.ex.hdf5 import File
from ontolutils.ex.m4i import Tool, NumericalVariable
from ontolutils.ex.prov import Activity
from ontolutils.ex.qudt import Unit
from ontolutils.ex.sosa import Sensor, Platform, Observation, Result
from ontolutils.ex.ssn import Accuracy, SystemCapability, MeasurementRange, ObservableProperty
from ontolutils.namespacelib import QUDT_KIND, QUDT_UNIT


class TestSosa(unittest.TestCase):

    def test_observable_property(self):
        oprop = ObservableProperty(
            id="http://example.org/observable_property/1",
            isObservedBy="http://example.org/sensor/1"
        )
        self.assertEqual(oprop.serialize("ttl"),
                         """@prefix sosa: <http://www.w3.org/ns/sosa/> .

<http://example.org/observable_property/1> a sosa:ObservableProperty ;
    sosa:isObservedBy <http://example.org/sensor/1> .

""")

    def test_sensor_as_an_agent_and_entity(self):
        s = Sensor(
            id="http://example.org/sensor/1",
            label="Test Sensor@en",
            observes="http://example.org/observable_property/1",
            name="Sensor XYZ",
            description="A sensor for testing purposes.@en",
            was_generated_by=Activity(
                id="http://example.org/activity/1",
            ),
            had_primary_source=File(
                id="http://example.org/file/1",
            )
        )
        self.assertEqual("""@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix hdf5: <http://purl.allotrope.org/ontologies/hdf5/1.8#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sosa: <http://www.w3.org/ns/sosa/> .

<http://example.org/sensor/1> a sosa:Sensor ;
    rdfs:label "Test Sensor"@en ;
    dcterms:description "A sensor for testing purposes.@en" ;
    prov:hadPrimarySource <http://example.org/file/1> ;
    prov:wasGeneratedBy <http://example.org/activity/1> ;
    sosa:observes <http://example.org/observable_property/1> ;
    foaf:name "Sensor XYZ" .

<http://example.org/activity/1> a prov:Activity .

<http://example.org/file/1> a hdf5:File .

""", s.serialize("ttl"))

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
@prefix schema: <https://schema.org/> .
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
    rdfs:comment "Max error bound (±1%FS) for range 0–250 Pa (FS=250 Pa)."@en ;
    schema:unitCode <http://qudt.org/vocab/unit/PA> ;
    schema:value 2.5e+00 .

<http://example.org/accuracy/2> a ssn_system:Accuracy ;
    rdfs:comment "Max error bound (±1%FS) for range 0–500 Pa (FS=500 Pa)."@en ;
    schema:unitCode <http://qudt.org/vocab/unit/PA> ;
    schema:value 5e+00 .

<http://example.org/measurement_range/1> a ssn_system:MeasurementRange ;
    schema:maxValue 2.5e+02 ;
    schema:minValue 0e+00 ;
    schema:unitCode <http://qudt.org/vocab/unit/PA> .

<http://example.org/measurement_range/2> a ssn_system:MeasurementRange ;
    schema:maxValue 5e+02 ;
    schema:minValue 0e+00 ;
    schema:unitCode <http://qudt.org/vocab/unit/PA> .

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

    def test_ssyn_system(self):
        from ontolutils.namespacelib import SSN_SYSTEM
        self.assertEqual(SSN_SYSTEM._NS, "http://www.w3.org/ns/ssn/systems/")
        self.assertEqual(SSN_SYSTEM.Condition, rdflib.URIRef("http://www.w3.org/ns/ssn/systems/Condition"))

    def test_observation(self):
        vfr = NumericalVariable(
            id="http://example.org/variable/1",
            hasNumericalValue=0.1,
            hasUnit="m**3/s"
        )
        dp = NumericalVariable(
            id="http://example.org/variable/2",
            hasNumericalValue=35.3,
            hasUnit="Pa"
        )
        result1 = Result(
            id="http://example.org/result/1",
            has_numerical_variable=vfr
        )
        self.assertEqual(
            result1.hasNumericalVariable,
            vfr
        )
        result2 = Result(
            id="http://example.org/result/2",
            has_numerical_variable=dp
        )

        feature_of_interest = Thing(
            id="http://example.org/feature_of_interest/1",
            label="Operation Point"
        )
        observation = Observation(
            id="http://example.org/observation/1",
            label="Operation Point",
            has_feature_of_interest=feature_of_interest,
            hasResult=[result1, result2],
            madeBySensor="http://example.org/sensor/1",
            observes="http://example.org/observable_property/1"
        )
        self.assertEqual("""@prefix m4i: <http://w3id.org/nfdi4ing/metadata4ing#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sosa: <http://www.w3.org/ns/sosa/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.org/observation/1> a sosa:Observation ;
    rdfs:label "Operation Point" ;
    sosa:hasFeatureOfInterest <http://example.org/feature_of_interest/1> ;
    sosa:hasResult <http://example.org/result/1>,
        <http://example.org/result/2> ;
    sosa:madeBySensor <http://example.org/sensor/1> .

<http://example.org/feature_of_interest/1> a owl:Thing ;
    rdfs:label "Operation Point" .

<http://example.org/result/1> a sosa:Result ;
    m4i:hasNumericalVariable <http://example.org/variable/1> .

<http://example.org/result/2> a sosa:Result ;
    m4i:hasNumericalVariable <http://example.org/variable/2> .

<http://example.org/variable/1> a m4i:NumericalVariable ;
    m4i:hasNumericalValue 1e-01 ;
    m4i:hasUnit <http://qudt.org/vocab/unit/M3-PER-SEC> .

<http://example.org/variable/2> a m4i:NumericalVariable ;
    m4i:hasNumericalValue 3.53e+01 ;
    m4i:hasUnit <http://qudt.org/vocab/unit/PA> .

""",
                         observation.serialize("ttl"))

    def test_get_by_qkind(self):
        op = Observation(
            id="https://example.org/observation/1",
            has_result=[
                Result(
                    id="https://example.org/result/vfr1",
                    hasNumericalVariable=NumericalVariable(
                        id="https://example.org/numvar/1",
                        hasUnit=QUDT_UNIT.M3_PER_HR,
                    )
                ),
                Result(
                    id="https://example.org/result/dp1",
                    has_numerical_variable=NumericalVariable(
                        id="https://example.org/numvar/2",
                        hasUnit=QUDT_UNIT.PA
                    )
                ),
                Result(
                    id="https://example.org/result/n1",
                    has_numerical_variable=NumericalVariable(
                        id="https://example.org/numvar/3",
                        hasUnit=QUDT_UNIT.PER_MIN
                    )
                ),
            ],
        )
        vfr = op.get_numerical_variable_by_kind_of_quantity(
            QUDT_KIND.VolumeFlowRate
        )
        self.assertEqual(1, len(vfr))
        self.assertEqual(vfr[0].hasUnit, op.hasResult[0].hasNumericalVariable.hasUnit)

    def test_observation_collection(self):
        obs1 = Observation(
            id="http://example.org/observation/1",
            label="Observation 1"
        )
        obs2 = Observation(
            id="http://example.org/observation/2",
            label="Observation 2"
        )
        from ontolutils.ex.sosa import ObservationCollection
        obs_collection = ObservationCollection(
            id="http://example.org/observation_collection/1",
            has_member=[obs1, obs2]
        )
        parent_collection = ObservationCollection(
            has_member=obs_collection
        )
        self.assertEqual(
            parent_collection.hasMember.hasMember[1].label, "Observation 2"
        )
        ttl = parent_collection.serialize("ttl")
        self.assertEqual(ttl, """@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sosa: <http://www.w3.org/ns/sosa/> .

<http://example.org/observation/1> a sosa:Observation ;
    rdfs:label "Observation 1" .

<http://example.org/observation/2> a sosa:Observation ;
    rdfs:label "Observation 2" .

<http://example.org/observation_collection/1> a sosa:ObservationCollection ;
    sosa:hasMember <http://example.org/observation/1>,
        <http://example.org/observation/2> .

[] a sosa:ObservationCollection ;
    sosa:hasMember <http://example.org/observation_collection/1> .

""")

    def test_observation_to_xarray(self):
        observation1 = Observation(
            label="observation1",
            has_result=[
                Result(
                    has_numerical_variable=NumericalVariable(
                        label=["pressure@en", "Druck@de"],
                        has_numerical_value=100,
                        has_unit=QUDT_UNIT.PA,
                        has_kind_of_quantity=QUDT_KIND.StaticPressure,
                    )
                )
            ]
        )
        # print(observation1.serialize("ttl"))
        da = observation1.to_xarray()
        # self.assertIsInstance(da, xr.DataArray)
        print(da)
        # da.pressure.plot.scatter()

    def test_observation_collection_to_xarray(self):

        observation2 = Observation(
            label="observation2",
            has_result=Result(
                has_numerical_variable=NumericalVariable(
                    label="vfr",
                    has_numerical_value=500,
                    has_unit=QUDT_UNIT.M3_PER_SEC,
                    has_kind_of_quantity=QUDT_KIND.VolumeFlowRate,
                )
            )
        )