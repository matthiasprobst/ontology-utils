import unittest

import pydantic

from ontolutils.ex.m4i import TextVariable, NumericalVariable, Tool, ProcessingStep
from ontolutils.ex.qudt import Unit


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

    def test_ProcessingStep(self):
        ps1 = ProcessingStep(
            id='http://example.org/processing_step/1',
        )
        ps2 = ProcessingStep(
            id='http://example.org/processing_step/2',
            precedes=ps1
        )
        self.assertEqual(ps2.precedes.id, 'http://example.org/processing_step/1')

        with self.assertRaises(pydantic.ValidationError):
            ProcessingStep(
                id='http://example.org/processing_step/2',
                precedes=Tool()
            )

    def testTextVariable(self):
        text_variable = TextVariable(
            hasStringValue='String value',
            hasVariableDescription='Variable description'
        )
        self.assertEqual(text_variable.hasStringValue, 'String value')
        self.assertEqual(text_variable.hasVariableDescription, 'Variable description')

    def testNumericalVariableWithoutStandardName(self):
        numerical_variable = NumericalVariable(
            hasUnit='mm/s',
            hasNumericalValue=1.0,
            hasMaximumValue=2.0,
            hasVariableDescription='Variable description')
        self.assertEqual(numerical_variable.hasUnit, 'http://qudt.org/vocab/unit/MilliM-PER-SEC')
        self.assertEqual(numerical_variable.hasNumericalValue, 1.0)
        self.assertEqual(numerical_variable.hasMaximumValue, 2.0)
        self.assertEqual(numerical_variable.hasVariableDescription, 'Variable description')

        numerical_variable2 = NumericalVariable(
            hasUnit=Unit(id='http://qudt.org/vocab/unit/M-PER-SEC', hasQuantityKind='Length'),
            hasNumericalValue=1.0,
            hasMaximumValue=2.0,
            hasVariableDescription='Variable description')
        self.assertEqual(str(numerical_variable2.hasUnit.id), 'http://qudt.org/vocab/unit/M-PER-SEC')
        self.assertEqual(numerical_variable2.hasNumericalValue, 1.0)
        self.assertEqual(numerical_variable2.hasMaximumValue, 2.0)
        self.assertEqual(numerical_variable2.hasVariableDescription, 'Variable description')
