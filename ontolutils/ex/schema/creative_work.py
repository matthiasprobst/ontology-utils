import json
import pathlib
from typing import Union, List, Optional

from ontolutils import namespaces, urirefs
from ontolutils.classes.utils import download_file
from pydantic import HttpUrl, field_validator, Field

from .thing import Thing


@namespaces(schema="https://schema.org/")
@urirefs(Organization='schema:Organization',
         name='schema:name')
class Organization(Thing):
    """schema:Organization (https://schema.org/Organization)"""


@namespaces(schema="https://schema.org/")
@urirefs(Person='schema:Person',
         givenName='schema:givenName',
         familyName='schema:familyName',
         email='schema:email',
         affiliation='schema:affiliation'
         )
class Person(Thing):
    """schema:Person (https://schema.org/Person)"""
    givenName: str = Field(alias="given_name")
    familyName: str = Field(alias="family_name", default=None)
    email: str = None
    affiliation: Union[Organization, List[Organization]] = Field(default=None)


@namespaces(schema="https://schema.org/")
@urirefs(CreativeWork='schema:CreativeWork',
         author='schema:author',
         abstract='schema:abstract')
class CreativeWork(Thing):
    """schema:CreativeWork (not intended to use for modeling)"""
    author: Union[Person, Organization, List[Union[Person, Organization]]] = Field(default=None)
    abstract: str  = Field(default=None)


@namespaces(schema="https://schema.org/")
@urirefs(SoftwareApplication='schema:SoftwareApplication',
         applicationCategory='schema:applicationCategory',
         downloadURL='schema:downloadURL',
         version='schema:version')
class SoftwareApplication(CreativeWork):
    """schema:SoftwareApplication (https://schema.org/SoftwareApplication)"""
    applicationCategory: Union[str, HttpUrl] = Field(default=None, alias="application_category")
    downloadURL: HttpUrl = Field(default=None, alias="download_URL")
    version: str = Field(default=None, alias="softwareVersion")

    @field_validator('applicationCategory')
    @classmethod
    def _validate_applicationCategory(cls, application_category: Union[str, HttpUrl]):
        if application_category.startswith('file:'):
            return application_category.rsplit('/', 1)[-1]
        return application_category


@namespaces(schema="https://schema.org/")
@urirefs(SoftwareSourceCode='schema:SoftwareSourceCode',
         codeRepository='schema:codeRepository',
         version='schema:version',
         applicationCategory='schema:applicationCategory')
class SoftwareSourceCode(CreativeWork):
    """Pydantic implementation of schema:SoftwareSourceCode (see https://schema.org/SoftwareSourceCode)

    .. note::

        More than the below parameters are possible but not explicitly defined here.
    """
    codeRepository: Union[HttpUrl, str] = Field(default=None, alias="code_repository")
    programmingLanguage: Optional[Union[str, List[str]]] = Field(default=None, alias="programming_language")
    applicationCategory: Union[str, HttpUrl] = Field(default=None, alias="application_category")
    version: str = Field(default=None)

    @classmethod
    def from_codemeta(cls, filename: Union[str, pathlib.Path]):
        """Create a SoftwareSourceCode instance from a codemeta.json file."""

        codemeta_context_file = download_file(
            'https://raw.githubusercontent.com/codemeta/codemeta/2.0/codemeta.jsonld',
            None)
        with open(codemeta_context_file) as f:
            codemeta_context = json.load(f)['@context']

        with open(filename, encoding='utf-8') as f:
            data = json.load(f)
        _ = data.pop('@context')
        data['@context'] = codemeta_context
        return SoftwareSourceCode.from_jsonld(data=json.dumps(data), limit=1)

    @field_validator('codeRepository')
    @classmethod
    def _validate_code_repository(cls, code_repository: Union[str, HttpUrl]):
        if not isinstance(code_repository, str):
            return code_repository
        if code_repository.startswith('git+'):
            _url = HttpUrl(code_repository.split("git+", 1)[1])
        return code_repository

    @field_validator('applicationCategory')
    @classmethod
    def _validate_applicationCategory(cls, application_category: Union[str, HttpUrl]):
        if application_category.startswith('file:'):
            return application_category.rsplit('/', 1)[-1]
        return application_category
