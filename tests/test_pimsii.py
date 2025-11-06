import unittest

from ontolutils.ex.pimsii import Property, Variable


class TestPIMSII(unittest.TestCase):

    def testVariable(self):
        variable = Variable(
            id="_:b1",
            label="my variable"
        )
        self.assertEqual(variable.serialize("ttl"), """@prefix pims: <http://www.molmod.info/semantics/pims-ii.ttl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

[] a pims:Variable ;
    rdfs:label "my variable" .

""")

    def testProperty(self):
        prop = Property(
            id="_:b1",
            label="my property",
            hasValue=5.4
        )
        print(prop.serialize("ttl"))
        self.assertEqual(prop.serialize("ttl"), """@prefix m4i: <http://w3id.org/nfdi4ing/metadata4ing#> .
@prefix pims: <http://www.molmod.info/semantics/pims-ii.ttl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

[] a pims:Property ;
    rdfs:label "my property" ;
    m4i:hasValue 5.4e+00 .

""")
