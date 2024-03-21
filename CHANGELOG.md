# Changelog

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