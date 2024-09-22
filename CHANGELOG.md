# Changelog

## v0.4.0
  - A blank ID is automatically assigned to a Thing if not provided during initialization

## v0.3.0
  - Add `validate_assignment=True`, so property assignments are validated against the schema

## v0.2.23
  - update `qudt_lookup`

## v0.2.22
  - add function `parse_unit`, which converts string to QUDT unit

## v0.2.21
  - pivmeta namespace is automatically generated from the context.jsonld file
  - bugfixes

## v0.2.20 - skipped

## v0.2.19 - skipped

## v0.2.18

- solving problem of changing ontologies which are under development by generating the
  context python files dynamically, which takes time but is better than having to update the package every time the

## v0.2.12 - v0.2.17

- updates according to changes in context.jsonld of the ontologies
- bugfixes

## v0.2.11

- Fixed duplicates in namespaces

## v0.2.10

- bugfixes serialization of json-ld

## v0.2.9

- attributes of Thing objects can be different to the ones defined in the schema. The user can decide whether to resolve
  this using prefixes in the JSON-LD file or adding a entry in the context dictionary.
- updated docstrings and documentation

## v0.2.8

- bugfix serialization of json-ld. context was not properly generated
- updated PIVMETA namespace

## v0.2.7

- bugfix schema.org namespace (https instead of http)
- bugfix NS in qudt_kind
- bugfix _dev.py

## v0.2.6

- removed default local namespace

## v0.2.0a2

- added documentation

## v0.2.0a1

- improved and consistent handling serialization

## v0.1.1

- bugfix exporting to jsond-ld
- bugfix query, now using data and source as arguments, which are passed to json.dump()

## v0.1.0

- initial version
- contains the following namespaces:
    - M4i
    - OBO
    - QUDT_UNIT
    - QUDT_QKIND
    - PIVMETA
    - SSNO
    - SCHEMA
    - CODEMETA