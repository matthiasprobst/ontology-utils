import pathlib
import unittest

from ontolutils.ex.m4i import NumericalVariable
from ontolutils.ex.sis import StandardMU, ExpandedMU, CoverageIntervalMU

__this_dir__ = pathlib.Path(__file__).parent


class TestSis(unittest.TestCase):

    def test_uncertainty(self):
        # e.g. volume flow rate uncertainty
        Qv_u = StandardMU(
            id="http://example.org/uncertainty/1",
            hasValueStandardMU=0.05
        )
        ttl = Qv_u.serialize("ttl")
        self.assertEqual("""@prefix sis: <https://ptb.de/sis/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.org/uncertainty/1> a sis:StandardMU ;
    sis:hasValueStandardMU 5e-02 .

""", ttl)

    def test_expanded_mu(self):
        dp_u = ExpandedMU(hasCoverageFactor="2",
                          hasCoverageProbability="0.95",
                          hasValueExpandedMU="12")  # ±12 Pa (k=2)
        ttl = dp_u.serialize("ttl")
        print(ttl)
        self.assertEqual("""@prefix sis: <https://ptb.de/sis/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

[] a sis:ExpandedMU ;
    sis:hasCoverageFactor 2e+00 ;
    sis:hasCoverageProbability 9.5e-01 ;
    sis:hasValueExpandedMU 1.2e+01 .

""", ttl)

    def test_coverage_interval_mu(self):
        P_u = CoverageIntervalMU(hasCoverageProbability="0.95",
                                 hasIntervalMax="1480",
                                 hasIntervalMin="1520",
                                 hasValueStandardMU="10")
        ttl = P_u.serialize("ttl")
        print(ttl)
        self.assertEqual("""@prefix sis: <https://ptb.de/sis/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

[] a sis:CoverageIntervalMU ;
    sis:hasCoverageProbability 9.5e-01 ;
    sis:hasIntervalMax 1.48e+03 ;
    sis:hasIntervalMin 1.52e+03 ;
    sis:hasValueStandardMU 1e+01 .

""", ttl)

    def test_pt100(self):
        pt100_accuracy = ExpandedMU(
            label="PT100 Temperature Sensor Accuracy@en",
            hasCoverageFactor="2",
            hasCoverageProbability="0.95",
            hasValueExpandedMU="0.25"
        )  # °C
        ttl = pt100_accuracy.serialize("ttl")
        print(ttl)

        value = 20.0  # °C
        numerical_value = NumericalVariable(
            label="Measured Pressure Value@en",
            hasNumericalValue=value,
            hasUnit="http://qudt.org/vocab/unit/DEG_C",
            hasUncertaintyDeclaration=pt100_accuracy
        )

        ttl = numerical_value.serialize("ttl")
        self.assertEqual("""@prefix m4i: <http://w3id.org/nfdi4ing/metadata4ing#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sis: <https://ptb.de/sis/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

[] a m4i:NumericalVariable ;
    rdfs:label "Measured Pressure Value"@en ;
    m4i:hasNumericalValue 2e+01 ;
    m4i:hasUncertaintyDeclaration [ a sis:ExpandedMU ;
            rdfs:label "PT100 Temperature Sensor Accuracy"@en ;
            sis:hasCoverageFactor 2e+00 ;
            sis:hasCoverageProbability 9.5e-01 ;
            sis:hasValueExpandedMU 2.5e-01 ] ;
    m4i:hasUnit <http://qudt.org/vocab/unit/DEG_C> .

""", ttl)

        # plt.figure()
        #
        # U = float(numerical_value.hasUncertaintyDeclaration.hasValueExpandedMU)
        # k = float(numerical_value.hasUncertaintyDeclaration.hasCoverageFactor)
        # u = U / k
        # plt.errorbar(
        #     x=[0],
        #     y=[numerical_value.hasNumericalValue],
        #     yerr=[numerical_value.hasUncertaintyDeclaration.hasValueExpandedMU],
        #     fmt='o',
        #     capsize=5,
        #     ecolor="blue",
        #     label=f"Measured Value with Standard Uncertainty (±{k}σ)"
        # )
        # plt.errorbar(
        #     x=[0],
        #     y=[numerical_value.hasNumericalValue],
        #     yerr=[u],
        #     fmt='o',
        #     capsize=5,
        #     color="orange",
        #     label=f"Measured Value with Standard Uncertainty (±1σ)"
        # )
        # plt.ylabel("Temperature [°C]")
        # plt.xticks([])
        # plt.legend()
        # plt.show()
