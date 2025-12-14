import pathlib
import unittest

from ontolutils.ex.qudt import Unit
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
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
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
    qudt:dbpediaMatch <http://dbpedia.org/resource/Pascal> ;
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
    rdfs:isDefinedBy <http://qudt.org/3.1.8/vocab/unit> ;
    skos:exactMatch <http://qudt.org/vocab/unit/KiloGM-PER-M-SEC2>,
        <http://qudt.org/vocab/unit/N-PER-M2> .

""",
            u_pa.serialize(format="ttl"))
