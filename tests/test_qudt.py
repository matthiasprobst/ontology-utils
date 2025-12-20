import pathlib
import unittest

from ontolutils.ex.qudt import Unit
from ontolutils.ex.qudt.conversion import convert_value_qudt, to_pint_unit
from ontolutils.ex.qudt.utils import iri2str
from ontolutils.namespacelib import QUDT_UNIT

__this_dir__ = pathlib.Path(__file__).parent.resolve()


class TestQudt(unittest.TestCase):

    def test_iri2str(self):
        str1 = iri2str[str(QUDT_UNIT.M)]
        self.assertEqual(str1, "m")

    def test_unit(self):
        pascal_ttl = __this_dir__ / "data" / "qudt_unit_pa.ttl"
        # g = rdflib.Graph().parse(pascal_ttl)
        # ttl = g.serialize(format="ttl")
        u_pa = Unit.from_file(pascal_ttl, format="ttl", limit=1)
        self.assertTrue("Pascal" in [str(l) for l in u_pa.label])
        print(u_pa.serialize(format="ttl"))
        self.assertEqual(
            """@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://qudt.org/vocab/unit/PA> a qudt:Unit ;
    rdfs:label "Pascal",
        "باسكال"@ar,
        "Паскал"@bg,
        "Pascal"@cs,
        "Pascal"@de,
        "Πασκάλ"@el,
        "Pascal"@en,
        "Pascal"@es,
        "پاسگال"@fa,
        "Pascal"@fr,
        "פסקל"@he,
        "पास्कल"@hi,
        "Pascal"@hu,
        "Pascal"@it,
        "パスカル"@ja,
        "Pascalium"@la,
        "Pascal"@ms,
        "Paskal"@pl,
        "Pascal"@pt,
        "Pascal"@ro,
        "Паскаль"@ru,
        "Pascal"@sl,
        "Pascal"@tr,
        "帕斯卡"@zh ;
    dcterms:description "The SI unit of pressure. The pascal is the standard pressure unit in the MKS metric system, equal to one newton per square meter or one \\"kilogram per meter per second per second.\\" The unit is named for Blaise Pascal (1623-1662), French philosopher and mathematician, who was the first person to use a barometer to measure differences in altitude." ;
    qudt:applicableSystem <http://qudt.org/vocab/sou/CGS>,
        <http://qudt.org/vocab/sou/CGS-EMU>,
        <http://qudt.org/vocab/sou/CGS-GAUSS>,
        <http://qudt.org/vocab/sou/SI> ;
    qudt:conversionMultiplier 1e+00 ;
    qudt:conversionMultiplierSN 1e+00 ;
    qudt:dbpediaMatch <http://dbpedia.org/resource/Pascal> ;
    qudt:exactMatch <http://qudt.org/vocab/unit/KiloGM-PER-M-SEC2>,
        <http://qudt.org/vocab/unit/N-PER-M2> ;
    qudt:hasDimensionVector <http://qudt.org/vocab/dimensionvector/A0E0L-1I0M1H0T-2D0> ;
    qudt:hasQuantityKind <http://qudt.org/vocab/quantitykind/BulkModulus>,
        <http://qudt.org/vocab/quantitykind/ForcePerArea>,
        <http://qudt.org/vocab/quantitykind/Fugacity>,
        <http://qudt.org/vocab/quantitykind/ModulusOfElasticity>,
        <http://qudt.org/vocab/quantitykind/ShearModulus>,
        <http://qudt.org/vocab/quantitykind/VaporPressure> ;
    qudt:hasReciprocalUnit <http://qudt.org/vocab/unit/M2-PER-N> ;
    qudt:iec61360Code "0112/2///62720#UAA258" ;
    qudt:informativeReference <http://en.wikipedia.org/wiki/Pascal?oldid=492989202>,
        <https://cdd.iec.ch/cdd/iec62720/iec62720.nsf/Units/0112-2---62720%23UAA258> ;
    qudt:omUnit <http://www.ontology-of-units-of-measure.org/resource/om-2/pascal> ;
    qudt:siExactMatch <https://si-digital-framework.org/SI/units/pascal> ;
    qudt:symbol "Pa" ;
    qudt:ucumCode "Pa" ;
    qudt:udunitsCode "Pa" ;
    qudt:uneceCommonCode "PAL" ;
    qudt:wikidataMatch <http://www.wikidata.org/entity/Q44395> ;
    rdfs:isDefinedBy <http://qudt.org/3.1.8/vocab/unit> .

""",
            u_pa.serialize(format="ttl"))

    def test_scaling_cm_to_m_and_back(self):
        m = Unit(
            id=QUDT_UNIT.M,
            conversionMultiplier=1.0,
            conversionOffset=0.0
        )
        cm = Unit(
            id=QUDT_UNIT.CentiM,
            scalingOf=m,
            conversionMultiplier=0.01,
            conversionOffset=0.0
        )
        convert_value_qudt(150, cm, m)
        self.assertEqual(
            convert_value_qudt(150, cm, m), 1.5
        )
        sec = Unit(
            id=QUDT_UNIT.SEC,
            conversionMultiplier=1.0,
            conversionOffset=0.0
        )
        minute = Unit(
            id=QUDT_UNIT.MIN,
            scalingOf=sec,
            conversionMultiplier=60.0,
            conversionOffset=0.0
        )
        self.assertEqual(
            convert_value_qudt(3, minute, sec), 180.0
        )
        self.assertEqual(
            convert_value_qudt(180, sec, minute), 3.0
        )
        kelvin = Unit(
            id=QUDT_UNIT.K,
            conversionMultiplier=1.0,
        )
        degC = Unit(
            id=QUDT_UNIT.DEG_C,
            conversionMultiplier=1.0,
            conversionOffset=273.15,
            scalingOf=kelvin,
        )
        self.assertEqual(
            convert_value_qudt(0, degC, kelvin), 273.15
        )
        self.assertEqual(
            convert_value_qudt(273.15, kelvin, degC), 0.0
        )

        # it should fail for incompatible units, e.g. degC to m
        with self.assertRaises(ValueError):
            convert_value_qudt(4.3, degC, m)

        # converting between identical units should return the same value
        self.assertEqual(
            convert_value_qudt(42.0, m, m), 42.0
        )

    def test_convert_to_pint_unit(self):
        u_pint = to_pint_unit(QUDT_UNIT.K)
        self.assertEqual(str(u_pint), "kelvin")
        u_pint = to_pint_unit(QUDT_UNIT.CentiM)
        self.assertEqual(str(u_pint), "centimeter")

        value = 25.0 * u_pint
        self.assertEqual(value.to("m").magnitude, 0.25)
        self.assertEqual(value.to("cm").magnitude, 25.0)

        u_pint_rev_per_min = to_pint_unit(QUDT_UNIT.PER_MIN)
        self.assertEqual(str(u_pint_rev_per_min), "1 / minute")

        u_pint_rev_per_min_base_units = (1 * u_pint_rev_per_min).to_base_units()
        self.assertEqual(str(u_pint_rev_per_min_base_units.units), "1 / second")

        u_pint_hertz = (600 * u_pint_rev_per_min).to("hertz")
        self.assertEqual(str(u_pint_hertz.units), "hertz")
        self.assertAlmostEqual(u_pint_hertz.magnitude, 10.0)
