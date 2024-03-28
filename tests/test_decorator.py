import logging
import unittest

from ontolutils import Thing, namespaces, urirefs
from ontolutils.classes import decorator

LOG_LEVEL = logging.DEBUG


class TestDecorator(unittest.TestCase):

    def test__is_http_url(self):
        self.assertFalse(decorator._is_http_url(123))
        self.assertFalse(decorator._is_http_url('123'))
        self.assertTrue(decorator._is_http_url('http://example.com'))

    def test_namespaces(self):
        with self.assertRaises(ValueError):
            @namespaces(invalid='Not_a_URI')
            class MyThing(Thing):
                """MyTHing"""

    def test_urirefs(self):
        with self.assertRaises(ValueError):
            @urirefs(name='http://example.com/name')
            class MyThing(Thing):
                """MyTHing"""
                name: str

        @namespaces(ex='http://example.com/')
        @urirefs(name='ex:name')
        class MyThing(Thing):
            """MyTHing"""
            name: str

        with self.assertRaises(TypeError):
            @urirefs(name=1.4)
            class MyThing(Thing):
                """MyTHing"""
                name: str
