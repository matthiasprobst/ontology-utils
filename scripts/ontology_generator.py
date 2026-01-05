#!/usr/bin/env python3
"""
Ontology to Python Code Generator

Generates Thing subclasses from RDF/OWL ontologies with proper type mapping,
inheritance handling, and validation rules.

Usage:
    python ontology_generator.py playground/hdf.ttl --output ontolutils/ex/generated_hdf5/
"""

import argparse
import logging
import pathlib
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from urllib.parse import urlparse

import rdflib
from rdflib import Graph, RDFS, RDF, OWL, XSD, URIRef

from ontolutils import Thing, namespaces, urirefs
from pydantic import Field

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Type mapping from RDF ranges to Python types
RANGE_TO_PYTHON = {
    str(XSD.string): "str",
    str(XSD.integer): "int",
    str(XSD.int): "int",
    str(XSD.long): "int",
    str(XSD.short): "int",
    str(XSD.byte): "int",
    str(XSD.nonNegativeInteger): "int",
    str(XSD.nonPositiveInteger): "int",
    str(XSD.positiveInteger): "int",
    str(XSD.negativeInteger): "int",
    str(XSD.float): "float",
    str(XSD.double): "float",
    str(XSD.decimal): "float",
    str(XSD.boolean): "bool",
    str(XSD.anyURI): "str",
    str(XSD.date): "datetime",
    str(XSD.dateTime): "datetime",
    str(XSD.time): "datetime",
}

# HDF5-specific custom types
CUSTOM_TYPE_MAPPING = {
    "HDF5Path": "HDF5Path",
    "rank": "Optional[int]",
    "size": "Optional[int]",
}


@dataclass
class PropertyInfo:
    """Information about an ontology property"""

    name: str
    uri: URIRef
    domain: Optional[URIRef]
    range: Optional[URIRef]
    is_functional: bool = False
    is_datatype_property: bool = True
    cardinality: Optional[str] = None
    min_cardinality: Optional[int] = None
    max_cardinality: Optional[int] = None
    constraints: Dict[str, Any] = None

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = {}


@dataclass
class ClassInfo:
    """Information about an ontology class"""

    name: str
    uri: URIRef
    parent: Optional[URIRef] = None
    properties: List[PropertyInfo] = None
    comment: Optional[str] = None
    label: Optional[str] = None
    is_abstract: bool = False

    def __post_init__(self):
        if self.properties is None:
            self.properties = []


class OntologyGenerator:
    """Main class for generating Python code from ontologies"""

    def __init__(self, ontology_file: str, base_class: str = "Thing"):
        self.ontology_file = pathlib.Path(ontology_file)
        self.base_class = base_class
        self.graph = Graph()
        self.namespaces = {}
        self.classes = {}
        self.properties = []

        # Load the ontology
        self._load_ontology()
        self._extract_namespaces()
        self._extract_classes()
        self._extract_properties()
        self._build_hierarchy()

    def _load_ontology(self):
        """Load the ontology file into rdflib Graph"""
        try:
            self.graph.parse(str(self.ontology_file), format="turtle")
            logger.info(f"Loaded ontology: {self.ontology_file}")
        except Exception as e:
            logger.error(f"Failed to load ontology: {e}")
            raise

    def _extract_namespaces(self):
        """Extract all namespaces from the ontology"""
        for prefix, namespace in self.graph.namespaces():
            self.namespaces[prefix] = str(namespace)
        logger.info(f"Found {len(self.namespaces)} namespaces")

    def _extract_classes(self):
        """Extract all classes from the ontology"""
        # Look for both RDFS and OWL classes
        class_types = {RDFS.Class, OWL.Class}

        for class_uri in self.graph.subjects():
            # Check if this is a class
            rdf_types = set(self.graph.objects(class_uri, RDF.type))
            if class_types.intersection(rdf_types):
                # Extract class name
                class_name = self._extract_name(class_uri)

                # Get parent class
                parent = self.graph.value(class_uri, RDFS.subClassOf)

                # Get comment and label
                comment = self._extract_comment(class_uri)
                label = self._extract_label(class_uri)

                self.classes[class_uri] = ClassInfo(
                    name=class_name,
                    uri=class_uri,
                    parent=parent,
                    comment=comment,
                    label=label,
                )

        logger.info(f"Found {len(self.classes)} classes")

    def _extract_properties(self):
        """Extract all properties from the ontology"""
        # Look for both RDF and OWL properties
        property_types = {RDF.Property, OWL.ObjectProperty, OWL.DatatypeProperty}

        for prop_uri in self.graph.subjects():
            rdf_types = set(self.graph.objects(prop_uri, RDF.type))
            if property_types.intersection(rdf_types):
                # Extract property name
                prop_name = self._extract_name(prop_uri)

                # Get domain and range
                domain = self.graph.value(prop_uri, RDFS.domain)
                range_uri = self.graph.value(prop_uri, RDFS.range)

                # Check if functional
                is_functional = (OWL.FunctionalProperty,) in rdf_types
                is_datatype = OWL.DatatypeProperty in rdf_types

                # Extract constraints
                constraints = self._extract_constraints(prop_uri)

                prop_info = PropertyInfo(
                    name=prop_name,
                    uri=prop_uri,
                    domain=domain,
                    range=range_uri,
                    is_functional=is_functional,
                    is_datatype_property=is_datatype,
                    constraints=constraints,
                )

                self.properties.append(prop_info)

                # Add property to relevant classes
                if domain and domain in self.classes:
                    self.classes[domain].properties.append(prop_info)

        logger.info(f"Found {len(self.properties)} properties")

    def _extract_constraints(self, prop_uri: URIRef) -> Dict[str, Any]:
        """Extract numeric constraints from property definitions"""
        constraints = {}

        # Look for XSD constraints
        for constraint_obj in self.graph.objects(prop_uri):
            # Check for owl:withRestrictions
            restrictions = list(
                self.graph.objects(constraint_obj, OWL.withRestrictions)
            )
            if restrictions:
                for restriction in restrictions[0]:
                    # Check for min/max constraints
                    min_vals = list(self.graph.objects(restriction, XSD.minInclusive))
                    max_vals = list(self.graph.objects(restriction, XSD.maxInclusive))

                    if min_vals:
                        constraints["ge"] = int(min_vals[0])
                    if max_vals:
                        constraints["le"] = int(max_vals[0])

        return constraints

    def _extract_name(self, uri: URIRef) -> str:
        """Extract a clean class/property name from URI"""
        uri_str = str(uri)

        # Handle fragment identifiers
        if "#" in uri_str:
            name = uri_str.split("#")[-1]
        # Handle path-based identifiers
        elif "/" in uri_str:
            name = uri_str.split("/")[-1]
        else:
            name = uri_str

        # Clean up the name
        name = re.sub(r"[^a-zA-Z0-9_]", "", name)

        # Ensure it starts with a letter
        if name and name[0].isdigit():
            name = f"_{name}"

        return name

    def _extract_comment(self, uri: URIRef) -> Optional[str]:
        """Extract rdfs:comment from a URI"""
        comments = list(self.graph.objects(uri, RDFS.comment))
        return str(comments[0]) if comments else None

    def _extract_label(self, uri: URIRef) -> Optional[str]:
        """Extract rdfs:label from a URI"""
        labels = list(self.graph.objects(uri, RDFS.label))
        return str(labels[0]) if labels else None

    def _get_namespace_prefix(self, uri: URIRef) -> str:
        """Get the namespace prefix for a URI"""
        uri_str = str(uri)

        for prefix, namespace in self.namespaces.items():
            if uri_str.startswith(namespace):
                return prefix

        # Try to extract from the URI itself
        if "#" in uri_str:
            base = uri_str.split("#")[0]
        else:
            base = "/".join(uri_str.split("/")[:-1]) + "/"

        # Look for matching namespace
        for prefix, namespace in self.namespaces.items():
            if base == namespace.rstrip("#/"):
                return prefix

        return "unknown"

    def _build_hierarchy(self):
        """Build inheritance hierarchy and order classes topologically"""
        # This is already handled by parent relationships in ClassInfo
        pass

    def _get_python_type(
        self, range_uri: Optional[URIRef], constraints: Dict[str, Any] = None
    ) -> str:
        """Convert RDF range to Python type string"""
        if not range_uri:
            return "str"

        range_str = str(range_uri)

        # Check for built-in XSD types
        if range_str in RANGE_TO_PYTHON:
            base_type = RANGE_TO_PYTHON[range_str]
        else:
            # Check if it's one of our classes
            if range_uri in self.classes:
                class_name = self.classes[range_uri].name
                base_type = f"AnyIriOf[{class_name}]"
            else:
                # Default to string for unknown types
                base_type = "str"

        # Apply constraints
        if constraints:
            if base_type == "str":
                return base_type
            elif base_type in ["int", "float"]:
                # Add Optional wrapper if there are constraints
                if any(k in constraints for k in ["ge", "le", "gt", "lt"]):
                    return f"Optional[{base_type}]"
                return base_type

        # Default to Optional for most properties
        return f"Optional[{base_type}]"

    def _generate_class_code(self, class_info: ClassInfo) -> List[str]:
        """Generate Python code for a single class"""
        lines = []

        # Get namespace info
        prefix = self._get_namespace_prefix(class_info.uri)
        namespace_uri = self.namespaces.get(prefix, "")

        # Skip invalid class names
        if not class_info.name or class_info.name.startswith("_"):
            return lines

        # Generate namespace decorator
        lines.append(f'@namespaces({prefix}="{namespace_uri}")')

        # Generate urirefs decorator
        uriref_lines = [f"@urirefs("]
        uriref_lines.append(f'    {class_info.name}="{prefix}:{class_info.name}",')

        # Add unique properties to urirefs
        seen_props = set()
        for prop in class_info.properties:
            if prop.name not in seen_props and prop.name != class_info.name:
                seen_props.add(prop.name)
                prop_prefix = self._get_namespace_prefix(prop.uri)
                uriref_lines.append(f'    {prop.name}="{prop_prefix}:{prop.name}",')

        uriref_lines.append(")")
        lines.extend(uriref_lines)

        # Generate class definition
        parent_name = self.base_class
        if class_info.parent and class_info.parent in self.classes:
            parent_name = self.classes[class_info.parent].name

        lines.append(f"class {class_info.name}({parent_name}):")

        # Generate docstring
        if class_info.comment:
            # Clean up docstring for Python
            docstring = class_info.comment.replace('"""', '\\"\\"\\"').replace(
                "\n", " "
            )
            if len(docstring) > 200:
                docstring = docstring[:197] + "..."
            lines.append(f'    """{docstring}"""')
        else:
            lines.append(f'    """{prefix}:{class_info.name}"""')

        # Generate properties
        if class_info.properties:
            # Group unique properties by name
            unique_props = {}
            for prop in class_info.properties:
                if prop.name not in unique_props:
                    unique_props[prop.name] = prop

            for prop in unique_props.values():
                prop_type = self._get_python_type(prop.range, prop.constraints)

                # Skip if prop type refers to invalid class
                if "n734277b6d29e433eb6db6c5e97a3ef15b25" in prop_type:
                    continue

                # Add field constraints
                field_args = ["default=None"]
                for constraint_name, constraint_value in prop.constraints.items():
                    field_args.append(f"{constraint_name}={constraint_value}")

                field_def = (
                    f"    {prop.name}: {prop_type} = Field({', '.join(field_args)})"
                )
                lines.append(field_def)

            lines.append("")
        else:
            lines.append("    pass")
            lines.append("")

        # Add custom validators for HDF5-specific cases
        if class_info.name in ["Dataset", "Group"]:
            lines.extend(self._generate_hdf5_validators(class_info.name))

        lines.append("")
        return lines

    def _generate_hdf5_validators(self, class_name: str) -> List[str]:
        """Generate custom validators for HDF5 classes"""
        validators = []

        if class_name == "Dataset":
            validators.extend(
                [
                    "",
                    "    @field_validator('name', mode='before')",
                    "    @classmethod",
                    "    def _validate_hdf5_path(cls, name):",
                    "        if isinstance(name, str) and not name.startswith('/'):",
                    "            raise ValueError('HDF5 path must start with /')",
                    "        return name",
                ]
            )

        elif class_name == "Group":
            validators.extend(
                [
                    "",
                    "    @field_validator('name', mode='before')",
                    "    @classmethod",
                    "    def _validate_hdf5_path(cls, name):",
                    "        if isinstance(name, str) and not name.startswith('/'):",
                    "            raise ValueError('HDF5 path must start with /')",
                    "        return name",
                ]
            )

        return validators

    def _generate_module_imports(self) -> List[str]:
        """Generate common imports for the module"""
        return [
            '"""',
            f"Generated Thing subclasses from {self.ontology_file.name}",
            "",
            "This file was automatically generated by ontology_generator.py",
            '"""',
            "",
            "from typing import Optional, Union, List, Any",
            "from datetime import datetime",
            "from pydantic import Field, field_validator",
            "from ontolutils import Thing, namespaces, urirefs",
            "from ontolutils.typing import AnyIriOf",
            "",
            "# Custom type validators for HDF5",
            "from typing_extensions import Annotated",
            "",
            "",
            "def _validate_hdf5_path(path: str, handler):",
            "    if isinstance(path, str) and not path.startswith('/'):",
            "        raise ValueError('HDF5 path must start with /')",
            "    return path",
            "",
            "",
            "HDF5Path = Annotated[str, _validate_hdf5_path]",
            "",
        ]

    def generate_models(self, output_dir: str, include_imports: bool = True):
        """Generate all Python model files"""
        output_path = pathlib.Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Main models file
        models_file = output_path / "models.py"

        with open(models_file, "w", encoding="utf-8") as f:
            # Write header imports
            if include_imports:
                f.write("from __future__ import annotations\n")
                f.write("\n".join(self._generate_module_imports()))
                f.write("\n")

            # Generate classes in hierarchy order
            for class_info in self._get_ordered_classes():
                class_code = self._generate_class_code(class_info)
                f.write("\n".join(class_code))
                f.write("\n\n")

            # Add model rebuild calls for all generated classes at the end
            f.write("\n# Rebuild all models to resolve forward references\n")
            for class_info in self._get_ordered_classes():
                f.write(f"{class_info.name}.model_rebuild()\n")

        logger.info(f"Generated models file: {models_file}")

        # Generate __init__.py
        init_file = output_path / "__init__.py"
        with open(init_file, "w", encoding="utf-8") as f:
            f.write('"""Generated Thing subclasses"""\n\n')

            # Export all classes
            class_names = [cls.name for cls in self.classes.values()]
            f.write(f"__all__ = {class_names}\n\n")

            # Import all classes
            for class_name in class_names:
                f.write(f"from .models import {class_name}\n")

        logger.info(f"Generated init file: {init_file}")

    def _get_ordered_classes(self) -> List[ClassInfo]:
        """Get classes ordered by inheritance hierarchy (parents before children)"""
        # Simple topological sort
        ordered = []
        visited = set()

        def visit(class_info: ClassInfo):
            if class_info.uri in visited:
                return
            visited.add(class_info.uri)

            # Visit parent first
            if class_info.parent and class_info.parent in self.classes:
                visit(self.classes[class_info.parent])

            ordered.append(class_info)

        for class_info in self.classes.values():
            visit(class_info)

        return ordered


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description="Generate Python Thing subclasses from RDF/OWL ontologies"
    )
    parser.add_argument(
        "ontology_file", help="Path to the ontology file (Turtle format)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="./generated_models",
        help="Output directory for generated models",
    )
    parser.add_argument(
        "--base-class", default="Thing", help="Base class for generated models"
    )
    parser.add_argument(
        "--include-imports",
        action="store_true",
        default=True,
        help="Include import statements in generated files",
    )

    args = parser.parse_args()

    # Generate models
    generator = OntologyGenerator(args.ontology_file, args.base_class)
    generator.generate_models(args.output, args.include_imports)

    print(f"Generated Thing subclasses from {args.ontology_file}")
    print(f"Output directory: {args.output}")


if __name__ == "__main__":
    main()
