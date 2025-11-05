from ontolutils import namespaces, urirefs
from .variable import Variable


@namespaces(pims="http://www.molmod.info/semantics/pims-ii.ttl#")
@urirefs(Property='pims:Property')
class Property(Variable):
    """Pydantic implementation of pims:Property"""
