from datetime import datetime
from typing import List, Union

from pydantic import Field

from ontolutils import Thing
from ontolutils import urirefs, namespaces
from ontolutils.typing import ResourceType


@namespaces(prov="http://www.w3.org/ns/prov#")
@urirefs(Activity='prov:Activity',
         startedAtTime='prov:startedAtTime',
         endedAtTime='prov:endedAtTime',
         used='prov:used',
         generated='prov:generated',
         wasStartedBy='prov:wasStartedBy',
         wasEndedBy='prov:wasEndedBy'
         )
class Activity(Thing):
    """Pydantic Model for http://www.w3.org/ns/prov#Activity"""
    startedAtTime: datetime = Field(default=None, alias="startedAtTime")
    endedAtTime: datetime = Field(default=None, alias="endedAtTime")
    used: Union[ResourceType, List[ResourceType]] = Field(default=None, alias="used")
    generated: Union[ResourceType, List[ResourceType]] = Field(default=None, alias="generated")
    wasStartedBy: Union[ResourceType, List[ResourceType]] = Field(default=None, alias="was_started_by")
    wasEndedBy: Union[ResourceType, List[ResourceType]] = Field(default=None, alias="was_ended_by")
