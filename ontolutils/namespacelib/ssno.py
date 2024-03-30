from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class LanguageExtension:
    pass

class SSNO(DefinedNamespace):
    # uri = "https://w3id.org/nfdi4ing/metadata4ing#"
    # Generated with None version 0.2.15
    # Date: 2024-03-30 11:42:27.233056
    _fail = True
    StandardName: URIRef  # ['StandardName']
    StandardNameTable: URIRef  # ['StandardNameTable']
    canonical_units: URIRef  # ['canonical units']
    contact: URIRef  # ['contact']
    definedIn: URIRef  # ['defined in']
    hasStandardName: URIRef  # ['has standard name']
    hasStandardNames: URIRef  # ['has standard names']
    ancillary_variables: URIRef  # ['ancillary variables']
    standard_name: URIRef  # ['standard name']

    _NS = Namespace("https://matthiasprobst.github.io/ssno#")

setattr(SSNO, "StandardName", SSNO.StandardName)
setattr(SSNO, "StandardNameTable", SSNO.StandardNameTable)
setattr(SSNO, "canonical_units", SSNO.canonical_units)
setattr(SSNO, "contact", SSNO.contact)
setattr(SSNO, "defined_in", SSNO.definedIn)
setattr(SSNO, "has_standard_name", SSNO.hasStandardName)
setattr(SSNO, "has_standard_names", SSNO.hasStandardNames)
setattr(SSNO, "ancillary_variables", SSNO.ancillary_variables)
setattr(SSNO, "standard_name", SSNO.standard_name)