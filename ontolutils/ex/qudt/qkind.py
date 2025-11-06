from ontolutils import Thing, namespaces, urirefs


@namespaces(qudt="http://qudt.org/schema/qudt/")
@urirefs(QuantityKind='qudt:QuantityKind')
class QuantityKind(Thing):
    """Implementation of qudt:QuantityKind"""
