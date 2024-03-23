from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class LanguageExtension:
    pass

class SSNO(DefinedNamespace):
    # uri = "https://w3id.org/nfdi4ing/metadata4ing#"
    # Generated with None version 0.2.10
    # Date: 2024-03-23 12:18:41.770713
    _fail = True
    StandardName: URIRef  # ['StandardName']
    StandardNameTable: URIRef  # ['StandardNameTable']
    contact: URIRef  # ['contact']
    definedInStandardNameTable: URIRef  # ['standard name table']
    hasStandardName: URIRef  # ['has standard name']
    has_standard_names: URIRef  # ['has standard names']
    quantityKind: URIRef  # ['kind of quantity']
    unit: URIRef  # ['canonical units']
    hasDOI: URIRef  # ['has doi']
    latexSymbol: URIRef  # ['has latex symbol']
    standard_name: URIRef  # ['standard name']

    _NS = Namespace("https://matthiasprobst.github.io/ssno#")

setattr(SSNO, "StandardName", SSNO.StandardName)
setattr(SSNO, "StandardNameTable", SSNO.StandardNameTable)
setattr(SSNO, "contact", SSNO.contact)
setattr(SSNO, "standard_name_table", SSNO.definedInStandardNameTable)
setattr(SSNO, "has_standard_name", SSNO.hasStandardName)
setattr(SSNO, "has_standard_names", SSNO.has_standard_names)
setattr(SSNO, "kind_of_quantity", SSNO.quantityKind)
setattr(SSNO, "canonical_units", SSNO.unit)
setattr(SSNO, "has_doi", SSNO.hasDOI)
setattr(SSNO, "has_latex_symbol", SSNO.latexSymbol)
setattr(SSNO, "standard_name", SSNO.standard_name)