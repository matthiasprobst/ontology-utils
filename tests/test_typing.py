import unittest

import pydantic

from ontolutils import set_logging_level
from ontolutils.classes import typing

set_logging_level('WARNING')


class TestNamespaces(unittest.TestCase):

    def test_blank_node(self):
        class MyModel(pydantic.BaseModel):
            blank_node: typing.BlankNodeType

        with self.assertRaises(pydantic.ValidationError):
            MyModel(blank_node='b1')

        with self.assertRaises(pydantic.ValidationError):
            MyModel(blank_node='_b1')

        MyModel(blank_node='_:b1')
