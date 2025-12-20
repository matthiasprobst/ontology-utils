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

    def test_to_pint(self):
        numerical_variable = NumericalVariable(
            hasUnit='mm/s',
            hasNumericalValue=1.0,
            hasMaximumValue=2.0,
            hasVariableDescription='Variable description')
        pint_quantity = numerical_variable.to_pint()
        self.assertEqual(pint_quantity.magnitude, 1.0)
        self.assertEqual(str(pint_quantity.units), 'millimeter / second')

        numerical_variable_array = NumericalVariable(
            hasUnit='mm/s',
            hasNumericalValue=[1.0, 2.0, 3.0],
            hasMaximumValue=5.0,
            hasVariableDescription='Variable description')
        pint_quantity_array = numerical_variable_array.to_pint()
        self.assertEqual(pint_quantity_array.magnitude.tolist(), [1.0, 2.0, 3.0])
        self.assertEqual(str(pint_quantity_array.units), 'millimeter / second')

        numerical_variable_from_pint = NumericalVariable.from_pint(pint_quantity)
        self.assertEqual(
            numerical_variable_from_pint.hasUnit,
            'http://qudt.org/vocab/unit/MilliM-PER-SEC'
        )
        self.assertEqual(numerical_variable_from_pint.hasNumericalValue, 1.0)

        numerical_variable_from_pint = NumericalVariable.from_pint(
            pint_quantity_array,
            id="http://example.org/variable/vfr",
            hasSymbol='vfr'
        )
        self.assertEqual(
            numerical_variable_from_pint.hasUnit,
            'http://qudt.org/vocab/unit/MilliM-PER-SEC'
        )
        self.assertEqual(numerical_variable_from_pint.hasNumericalValue, [1.0, 2.0, 3.0])
        self.assertEqual(numerical_variable_from_pint.hasSymbol, 'vfr')
        ttl = numerical_variable_from_pint.serialize("ttl")
        self.assertEqual(ttl, """@prefix m4i: <http://w3id.org/nfdi4ing/metadata4ing#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://example.org/variable/vfr> a m4i:NumericalVariable ;
    m4i:hasNumericalValue 1e+00,
        2e+00,
        3e+00 ;
    m4i:hasSymbol "vfr" ;
    m4i:hasUnit <http://qudt.org/vocab/unit/MilliM-PER-SEC> .

""")

    def test_to_xarray(self):
        numerical_variable = NumericalVariable(
            id='http://example.org/variable/vfr',
            label=["Volume Flow Rate@en", "Volumenstrom@de", "Débit volumiqu"],
            hasUnit='mm/s',
            hasNumericalValue=[1.0, 2.0, 3.0],
            hasVariableDescription='Variable description',
            hasSymbol='vfr'
        )
        ttl_orig = numerical_variable.serialize("ttl")
        xarray_dataarray = numerical_variable.to_xarray(language="de")
        self.assertEqual(xarray_dataarray.has_symbol, 'vfr')
        self.assertEqual(xarray_dataarray.attrs['has_variable_description'], 'Variable description')
        self.assertEqual(xarray_dataarray.attrs['units'], 'mm/s')
        self.assertEqual(xarray_dataarray.values.tolist(), [1.0, 2.0, 3.0])

        # convert back to NumericalVariable
        numerical_variable_from_xarray = NumericalVariable.from_xarray(
            xarray_dataarray
        )
        ttl_after_conversions = numerical_variable_from_xarray.serialize("ttl")
        self.assertEqual(ttl_orig, ttl_after_conversions)
