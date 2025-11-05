import ontolutils
from ontolutils import namespaces, urirefs
from pydantic import HttpUrl


@namespaces(schema="https://schema.org/")
@urirefs(Thing='schema:Thing',
         description='schema:description',
         name='schema:name',
         url='schema:url')
class Thing(ontolutils.Thing):
    """schema:Thing (https://schema.org/Thing)
    The most generic type of item."""
    description: str = None
    url: HttpUrl = None
    name: str = None
