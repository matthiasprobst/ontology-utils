# Changelog

## v0.16.0
- upgrade setuptools due to CVE. For that reason, the python version
  requirement is now >=3.9

## v0.15.0

- Thing class got three new fields: `dcterms:relation`, `skos:closeMatch`, and `skos:exactMatch`

## v0.14.2

- add some more unit translations to dictionary `qudt_lookup`

## v0.14.1

- add missing adjustments to really fix parsing model from JSON-LD

## v0.14.0

- fix foaf namespace URL
- ~~fix parsing model from JSON-LD~~

## v0.13.3

- fix ontology builds by considering the owl named individuals
- fix hdf5 ontology build
- fix illegal characters in class and property names in schema.org

## v0.13.2

- bugfix HDF5 ontology. Data properties were missing

## v0.13.1

- build() is now also available as classmethod
- updated HDF5 namespace class
- add experimental generation of python Thing classes from an ontology

## v0.13.0

- own ontology classes can be built using the `build()` function. See Readme for more information.

## v0.12.5

- fix type hint
- add `serialize()` to allow serialization to more than just JSON-LD

## v0.12.4

- Hotfix for overwriting id by another field

## v0.12.3

- Hotfix for http://schema.org

## v0.12.2

- Bugfix owl namespace URL

## v0.12.1

- Bugfix missing OBO predicates

## v0.12.0

- Allow to set a default prefix for blank nodes.

## v0.11.0

- Undo more https fixes where it was not necessary

## v0.10.0

- Undo https fixes where it was not necessary

## v0.9.0

- Fix http to https in namespaces

## v0.8.0

- Added `HDF5` Ontology from the Allotrope Foundation (http://purl.allotrope.org/ontologies/hdf5/1.8#)

## v0.7.1

- If a potentially wrong ID is used through `id_as()` a `UserWarning` is raised, not an Error.

## v0.7.0

- Removed `use_as_id`. Instead, using `model_validator`. This ensures correct behaviour also for nested Things.

## v0.6.2

- Using a field for the @id tag must be set via `Field(..., json_schema_extra={'use_as_id': True})`

## v0.6.1

- removing print statement and fixing docstrings

## v0.6.0

- remove namespace SSNO and PIVMETA as they are not general enough to be part of the package

## v0.5.1

- Fixing the README

## v0.5.0

- Allowing to address alias fields instead of only the original field name
- Restricting depending on pacakge versions to a lower bound

## v0.4.8

- Add more entries to qudt lookup table

## v0.4.7

- use_as_id=True in Field() will use the value as ID if available

## v0.4.6

- Hotfix parsing JSON-LD data to instantiate a Thing object

## v0.4.5

- Bugfix parsing JSON-LD data to instantiate a Thing object

## v0.4.4

- Indentation can be defined for model_dump_jsonld(). Default is 4.

## v0.4.3

- Cause a KeyError if unit is not available in lookup table

## v0.4.2

- Bugfix in qudt lookup table.

## v0.4.1

- Bugfix considering extra fields in constructing the `__repr__` method of the `Thing` class

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