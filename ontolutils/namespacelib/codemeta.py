from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class LanguageExtension:
    pass

class CODEMETA(DefinedNamespace):
    # uri = "https://w3id.org/nfdi4ing/metadata4ing#"
    # Generated with None version 0.2.16
    # Date: 2024-04-08 15:01:30.249226
    _fail = True
    softwareSuggestions: URIRef  # ['softwareSuggestions']
    contIntegration: URIRef  # ['contIntegration']
    buildInstructions: URIRef  # ['buildInstructions']
    developmentStatus: URIRef  # ['developmentStatus']
    embargoDate: URIRef  # ['embargoDate']
    funding: URIRef  # ['funding']
    readme: URIRef  # ['readme']
    issueTracker: URIRef  # ['issueTracker']
    referencePublication: URIRef  # ['referencePublication']
    maintainer: URIRef  # ['maintainer']

    _NS = Namespace("https://codemeta.github.io/terms/")

setattr(CODEMETA, "softwareSuggestions", CODEMETA.softwareSuggestions)
setattr(CODEMETA, "contIntegration", CODEMETA.contIntegration)
setattr(CODEMETA, "buildInstructions", CODEMETA.buildInstructions)
setattr(CODEMETA, "developmentStatus", CODEMETA.developmentStatus)
setattr(CODEMETA, "embargoDate", CODEMETA.embargoDate)
setattr(CODEMETA, "funding", CODEMETA.funding)
setattr(CODEMETA, "readme", CODEMETA.readme)
setattr(CODEMETA, "issueTracker", CODEMETA.issueTracker)
setattr(CODEMETA, "referencePublication", CODEMETA.referencePublication)
setattr(CODEMETA, "maintainer", CODEMETA.maintainer)