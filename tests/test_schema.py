import logging
import unittest
from typing import Union

from pydantic import Field, HttpUrl

from ontolutils import Thing, urirefs, namespaces

LOG_LEVEL = logging.DEBUG


class TestSchema(unittest.TestCase):

    def testSchemaHTTP(self):
        @namespaces(schema="https://schema.org/")
        @urirefs(SoftwareSourceCode='schema:SoftwareSourceCode',
                 code_repository='schema:codeRepository',
                 application_category='schema:applicationCategory')
        class SoftwareSourceCode(Thing):
            """Pydantic Model for https://schema.org/SoftwareSourceCode"""
            code_repository: Union[HttpUrl, str] = Field(default=None, alias="codeRepository")
            application_category: Union[str, HttpUrl] = Field(default=None, alias="applicationCategory")

        thing = SoftwareSourceCode.from_jsonld(data={
            "@id": "_:N123",
            "@type": "http://schema.org/SoftwareSourceCode",  # note, it is http instead of https!
            "codeRepository": "https://example.com/code",
            "applicationCategory": "https://example.com/category"
        })
        print(thing[0].model_dump_jsonld(indent=2))
