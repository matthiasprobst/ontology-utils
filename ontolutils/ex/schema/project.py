from typing import Union, Optional, List

from pydantic import HttpUrl, field_validator, Field
from pydantic import model_validator

from ontolutils import Thing, namespaces, urirefs, as_id, LangString
from ontolutils.ex.prov import Organization, Person
from ontolutils.typing import ResourceType


@namespaces(schema="https://schema.org/")
@urirefs(
    Project='schema:Project',
    name='schema:name',
    identifier='schema:identifier',
    funder='schema:funder'
)
class Project(Thing):
    """Implementation of schema:Project"""
    name: Optional[Union[LangString, List[LangString]]] = Field(default=None)
    identifier: Optional[ResourceType] = Field(default=None)
    funder: Optional[Union[Person, Organization]] = Field(default=None)

    @model_validator(mode="before")
    def _change_id(self):
        return as_id(self, "identifier")

    @field_validator('identifier', mode='before')
    @classmethod
    def _identifier(cls, identifier):
        HttpUrl(identifier)
        return str(identifier)


@urirefs(ResearchProject='schema:ResearchProject')
class ResearchProject(Project):
    """Pydantic Model for schema:ResearchProject

    .. note::

        More than the below parameters are possible but not explicitly defined here.


    Parameters
    ----------
    tbd
    """

    def _repr_html_(self) -> str:
        """Returns the HTML representation of the class"""
        return f"{self.__class__.__name__}({self.identifier})"
