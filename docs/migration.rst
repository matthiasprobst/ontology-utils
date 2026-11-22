Migrating from 0.27 to 1.0
==========================

This page describes behavior changes that may require application updates.
Python 3.11 or newer is required; Python 3.10 is no longer supported.

RDF values and model projection
-------------------------------

Unconstrained model fields retain RDFLib ``Literal`` objects during RDF loading;
their JSON-LD serialization includes explicit datatype/language metadata.
Constrained Python fields still apply their declared validation and conversion.
Ordinary string fields are literal text, even when they resemble absolute or
compact IRIs. Resource references require explicit IRI/URL types or RDFLib
resource terms in unconstrained fields. The IRI validators preserve reference
meaning in string-compatible values and reject RDFLib literals; BNode references
retain their ``_:`` prefix. This replaces implicit URL/prefix guessing at export.
Python ``datetime`` values always serialize as ``xsd:dateTime``, including
midnight; time, fractional seconds and supplied UTC offsets are retained. Naive
datetimes remain without a timezone; the library does not infer one.
Nonfinite Python floats use explicit ``xsd:double`` value objects, keeping NaN
and infinities out of JSON number tokens. Direct JSON-LD, RDFLib reserialization
and combined graph export retain these values. Finite graph serialization keeps
the ordinary RDFLib path; nonfinite JSON-LD graphs use strict encoding before a
native JSON encoder can replace or emit these values incorrectly.
RDFLib parsing may normalize lexical forms of recognized datatypes; retain the
original document when byte-for-byte lexical preservation is required.
Model loading matches complete registered predicate IRIs, including nested
models. Identical local names in different namespaces remain distinct. Unknown
predicates cannot populate a mapped field through a local-name match. Per-load
namespace context is local to that operation and does not mutate model mappings.
Loading projects a graph onto registered model predicates; unmapped predicates
are omitted. Retain the source RDFLib graph when arbitrary triples must survive.
JSON-LD loading preserves HTTP vocabulary IRIs and literal text. Applications using HTTP schema.org data must map those exact IRIs or
perform an explicit, reviewed vocabulary migration before model loading.

Numerical RDF export preserves the original variable's identity in
every format; automatic scalar expansion with suffixed IDs is removed. Its
multi-valued numerical property is an unordered set, not an array encoding:
order, duplicates, shape, dtype and empty-versus-unset distinctions do not survive
an RDF round trip. Keep arrays in a suitable scientific data format, or model
individual scalar resources and their relationships explicitly. Pydantic and SHACL validation do not establish scientific validity.

RDF collection loading follows the requested head's ``rdf:rest`` chain and
preserves order and duplicate entries. Finite sequence loading requires exactly
one ``rdf:first`` and ``rdf:rest`` per cell, a resource-valued rest pointer, and
termination at ``rdf:nil``. Ambiguous or cyclic structures raise ``ValueError``;
this loading constraint does not classify the underlying graph as invalid RDF.

Resource expansion retains blank-node identifiers and represents cycle edges as
identifier references. Model fields on cyclic relationships must accept such
references. Shared nodes retain their identifiers across expanded branches;
expansion does not promise Python object identity.
Dictionary queries retain all RDF type assertions. Model loading projects onto
the requested Python class and its registered predicates; it does not promise
to preserve additional source type assertions when that model is serialized.
Dictionary-query resource references use ``{"@id": ...}`` objects rather than
plain strings. RDF collections retain explicit first/rest cells, including head
identifiers and annotations, instead of being flattened into Python lists.
This changes traversal of earlier dictionary results: a one-author collection
is accessed through ``result['author']['first']``. Use RDFLib's ``Collection``
against the parsed result graph for general ordered-list traversal.
Dictionary traversal is iterative and describes each reachable resource once.
Repeated edges use identifier references. Deep descriptions are emitted through
JSON-LD 1.1 ``@included`` with bounded inline nesting, so the output layout must
not be treated as a fixed Python object tree. Parse the result as RDF when
following references or processing arbitrarily deep graphs.

Mailboxes, units and loading results
------------------------------------

FOAF and PROV mailbox fields retain validated email strings in Python, including
their existing input aliases. They also accept ``mailto:`` strings and RDF IRIs.
RDF exports now emit ``foaf:mbox <mailto:address>``. Legacy email literals remain
accepted on input. Applications comparing earlier RDF output must account for
this correction from a literal to a mailbox resource.

Unit conversion compares base-unit resource identifiers independently of labels
and other descriptive metadata. Conflicting numerical factors on descriptions
of the same base unit raise ``ValueError``. Multiple ``scalingOf`` descriptions
require explicit selection before conversion, so list order cannot select the
conversion target.

QUDT conversion coefficients use ``reference = (value + offset) * multiplier``.
Offsets are applied before multiplication, correcting Fahrenheit conversions.
Coefficients refer to reference coordinates, rather than successive
``scalingOf`` edges: milligrams use ``1e-6`` and grams ``1e-3`` relative to
kilograms. Their factors must not be multiplied along the chain. The converter
uses the chain to establish a common root and applies the source and target
coefficients once each. A missing multiplier on a scaled unit, zero or
non-finite multipliers, and non-finite offsets raise ``ValueError`` instead of
silently assuming a conversion. This API converts absolute values, including
absolute temperatures; it does not convert temperature differences.

See QUDT's `Fahrenheit description <https://qudt.org/vocab/unit/DEG_F>`_ and
`milligram description <https://qudt.org/vocab/unit/MilliGM>`_ for the reference
coefficients. These are implementation corrections, not changes to QUDT data.

All model loaders limit complete resources rather than individual SPARQL rows.
They return a list by default, a single matching model for ``limit=1``, and
``[]`` for no matches or ``limit=0``. Negative limits raise ``ValueError``;
non-integer limits, including booleans, raise ``TypeError``. In particular,
``from_graph(limit=1)`` no longer returns a one-element list or truncates a
multi-valued field. Use ``create_query`` and RDFLib's ``graph.query`` when a
SPARQL row limit is intended. ``from_graph`` reads the supplied graph without
changing its triples or namespace bindings; its legacy ``distinct`` argument
is accepted, but resource descriptions are always unique. Selection order is
unspecified, so use an explicit ordered SPARQL query when order matters.
RDF loading supplies a list for fields declared as ``List[T]`` or
``Optional[List[T]]``, including nested fields with only one RDF value. This
accommodation applies to mapped RDF predicates; ordinary Python field input
still follows its declared Pydantic validation rules.
