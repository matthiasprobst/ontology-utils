from pydantic import HttpUrl

from ontolutils import namespaces, urirefs, Thing as BaseThing


@namespaces(schema="https://schema.org/")
@urirefs(Thing='schema:Thing',
         description='schema:description',
         name='schema:name',
         url='schema:url')
class Thing(BaseThing):
    """schema:Thing (https://schema.org/Thing)
    The most generic type of item."""
    description: str = None
    url: HttpUrl = None
    name: str = None
