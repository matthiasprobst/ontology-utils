import unittest

from ontolutils.ex.m4i import TextVariable, NumericalVariable, Tool


class TestM4i(unittest.TestCase):

    def test_tool(self):
        tool = Tool(
            id='http://example.org/tool/1',
            manufacturer="http://example.org/org/1",
        )
        self.assertEqual(tool.serialize("ttl"), """@prefix m4i: <http://w3id.org/nfdi4ing/metadata4ing#> .
@prefix pivmeta: <https://matthiasprobst.github.io/pivmeta#> .
@prefix prov: <http://www.w3.org/ns/prov#> .

<http://example.org/tool/1> a m4i:Tool ;
    pivmeta:manufacturer <http://example.org/org/1> .

<http://example.org/org/1> a prov:Organization .

""")

    def testTextVariable(self):
        text_variable = TextVariable(
            hasStringValue='String value',
            hasVariableDescription='Variable description'
        )
        self.assertEqual(text_variable.hasStringValue, 'String value')
        self.assertEqual(text_variable.hasVariableDescription, 'Variable description')

    def testNumericalVariableWithoutStandardName(self):
        numerical_variable = NumericalVariable(
            hasUnit='m/s',
            hasNumericalValue=1.0,
            hasMaximumValue=2.0,
            hasVariableDescription='Variable description')
        self.assertEqual(numerical_variable.hasUnit, 'http://qudt.org/vocab/unit/M-PER-SEC')
        self.assertEqual(numerical_variable.hasNumericalValue, 1.0)
        self.assertEqual(numerical_variable.hasMaximumValue, 2.0)
        self.assertEqual(numerical_variable.hasVariableDescription, 'Variable description')
