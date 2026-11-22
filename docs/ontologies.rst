Built-in ontology profiles
==========================

Built-in models are curated application profiles: selected classes and fields
with Python validation, aliases and conversion behavior. They do not implement
every term or constraint of the source ontology. A module's ``__version__`` is
its declared upstream baseline, not evidence that every mapping was audited.
The Python API, namespace constants, unit-symbol lookup and downloaded ontology
graphs are separate artifacts and need compatible provenance.

Vocabulary baselines and offline use
------------------------------------

Models and namespace constants do not refresh automatically at import,
installation or validation. A stable term IRI does not imply an unchanging
definition or a complete implementation of its ontology.

QUDT expansion now uses the 3.1.9 source vocabularies at commit
``cf953bf42846f28c6b40a71a74763b2ab1d92069``, matching the model baseline.
``ontolutils.ex.qudt.utils`` records URLs and SHA-256 digests; downloaded bytes
are checked before parsing. Requests have connection/read timeouts and successful
graphs are cached in memory. Initial expansion still requires network access;
for offline use, load a locally archived graph with ``Unit.from_graph`` or
``QuantityKind.from_graph``. Preserve the archive and its checksum with research
provenance. QUDT source licensing is CC BY 4.0; attribute QUDT.org when archiving
or redistributing vocabulary material.

Unit-to-quantity-kind associations may contain multiple values. The singular
``get_quantity_kind(Unit(...))`` helper requires one distinct associated kind;
otherwise pass the intended quantity-kind IRI explicitly. RDF triple order and
shared physical dimensions cannot select the meaning of a measurement.
``Unit(has_quantity_kind="Length")`` expands the bare local name to
``http://qudt.org/vocab/quantitykind/Length``. Lists use the same expansion per
entry. Explicit IRIs and QuantityKind models retain their identity; this local
convenience does not check whether a term exists in the vocabulary. Malformed
local names and RDF literals cannot be used as quantity-kind references.
The Wikidata field's canonical alias is ``wikidata_match``; the old input alias
with a trailing space remains accepted, but alias serialization uses the
corrected name.
Lookups cache internal results by normalized IRI and return independent model
copies. Changing a returned model does not alter later lookup results; a Unit's
current quantity-kind associations are checked on every singular-kind lookup.
QUDT source references can be ``xsd:anyURI`` literals. ``dbpediaMatch`` and
``informativeReference`` preserve these literals and their datatype rather than
turning them into RDF resource terms. Explicit resource references remain
accepted by this application profile. URL-shaped literal text is not evidence
that a property value is an IRI node.

Schema.org interoperability
---------------------------

Schema.org publishes HTTP and HTTPS vocabulary forms. These are distinct
RDF IRIs. Ontolutils matches the exact registered class and predicate IRIs;
it does not rewrite one form into the other. When combining data using both
forms, map the source IRIs explicitly or perform a vocabulary migration on
RDF terms. Document-wide text replacement can corrupt literal text and
unrelated resource identifiers.

Numerical value profiles
------------------------

The Metadata4Ing model retains its reviewed 1.4.0 baseline. That release defines
``hasNumericalValue`` as a datatype property, not an RDF collection relationship.
Do not attach an RDF list node to it merely to preserve a Python array's order.
NumericalVariable export uses repeated literal values on the original resource,
with RDF set semantics. This is a lossy metadata projection, not an array storage
format or a claim of complete ontology/range conformance. Scientific array data
and its dtype/shape/ordering need a suitable data format and explicit provenance.

Sources
-------

* `QUDT 3.1.9 release <https://github.com/qudt/qudt-public-repo/releases/tag/v3.1.9>`_
* `QUDT current vocabulary/provenance <https://qudt.org/doc/DOC_VOCAB-UNITS.html>`_
* `Schema.org developer guidance <https://schema.org/docs/developers.html>`_
* `DCAT 3 Recommendation <https://www.w3.org/TR/2024/REC-vocab-dcat-3-20240822/>`_
* `Metadata4Ing 1.4.0 <https://nfdi4ing.pages.rwth-aachen.de/metadata4ing/metadata4ing/1.4.0/index.html>`_
* `RDF graph set semantics <https://www.w3.org/TR/rdf11-concepts/#section-rdf-graph>`_
