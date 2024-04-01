from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class LanguageExtension:
    pass

class SSNO(DefinedNamespace):
    # uri = "https://w3id.org/nfdi4ing/metadata4ing#"
    # Generated with None version 0.2.15
    # Date: 2024-03-30 18:33:59.106931
    _fail = True
    StandardName: URIRef  # ['StandardName']
    StandardNameTable: URIRef  # ['StandardNameTable']
    canonicalUnits: URIRef  # ['canonical units']
    contact: URIRef  # ['contact']
    hasStandardName: URIRef  # ['has standard name']
    isStandardNameOf: URIRef  # ['is standard name of']
    standardNameTable: URIRef  # ['standard name table']
    standardNames: URIRef  # ['standard names']
    ancillaryVariables: URIRef  # ['ancillary variables']
    description: URIRef  # ['description']
    standardName: URIRef  # ['standard name']

    _NS = Namespace("https://matthiasprobst.github.io/ssno#")

setattr(SSNO, "StandardName", SSNO.StandardName)
setattr(SSNO, "StandardNameTable", SSNO.StandardNameTable)
setattr(SSNO, "canonical_units", SSNO.canonicalUnits)
setattr(SSNO, "contact", SSNO.contact)
setattr(SSNO, "has_standard_name", SSNO.hasStandardName)
setattr(SSNO, "is_standard_name_of", SSNO.isStandardNameOf)
setattr(SSNO, "standard_name_table", SSNO.standardNameTable)
setattr(SSNO, "standard_names", SSNO.standardNames)
setattr(SSNO, "ancillary_variables", SSNO.ancillaryVariables)
setattr(SSNO, "description", SSNO.description)
setattr(SSNO, "standard_name", SSNO.standardName)