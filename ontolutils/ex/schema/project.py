from datetime import datetime
from typing import Union, List

from ontolutils import Thing, namespaces, urirefs
from ..prov import Organization, Person


@namespaces(schema="https://schema.org/")
@urirefs(Project='schema:Research',
         identifier='schema:identifier',
         startDate='schema:startDate',
         endDate='schema:endDate',
         participant='schema:participant')
class Project(Thing):
    """Pydantic Model for schema:Project"""
    identifier: str
    startDate: datetime
    endDate: datetime
    participant: Union[Person, Organization, List[Union[Person, Organization]]]


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
        return f"{self.__class__.__name__}({self.mbox})"
