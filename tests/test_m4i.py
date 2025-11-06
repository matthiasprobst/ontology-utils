import unittest


from ontolutils.ex.m4i import TextVariable, NumericalVariable


class TestM4i(unittest.TestCase):

    def testTextVariable(self):
        text_variable = TextVariable(
            hasStringValue='String value',
            hasVariableDescription='Variable description'
        )
        self.assertEqual(text_variable.hasStringValue, 'String value')
        self.assertEqual(text_variable.hasVariableDescription, 'Variable description')

    def testNumericalVariableWithoutStandardName(self):
        numerical_variable = NumericalVariable(
            hasUnit='Unit',
            hasNumericalValue=1.0,
            hasMaximumValue=2.0,
            hasVariableDescription='Variable description')
        self.assertEqual(numerical_variable.hasUnit, 'Unit')
        self.assertEqual(numerical_variable.hasNumericalValue, 1.0)
        self.assertEqual(numerical_variable.hasMaximumValue, 2.0)
        self.assertEqual(numerical_variable.hasVariableDescription, 'Variable description')

