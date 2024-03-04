from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class LanguageExtension:
    pass

class SSNO(DefinedNamespace):
    # uri = "https://w3id.org/nfdi4ing/metadata4ing#"
    # Generated with namespacelib version 0.3.0
    # Date: 2024-03-02 13:35:55.978159
    _fail = True
    StandardName: URIRef  # ['StandardName']
    StandardNameTable: URIRef  # ['StandardNameTable']
    contact: URIRef  # ['contact']
    definedInStandardNameTable: URIRef  # ['standard name table']
    has_standard_names: URIRef  # ['standard names']
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
setattr(SSNO, "standard_names", SSNO.has_standard_names)
setattr(SSNO, "kind_of_quantity", SSNO.quantityKind)
setattr(SSNO, "canonical_units", SSNO.unit)
setattr(SSNO, "has_doi", SSNO.hasDOI)
setattr(SSNO, "has_latex_symbol", SSNO.latexSymbol)
setattr(SSNO, "standard_name", SSNO.standard_name)