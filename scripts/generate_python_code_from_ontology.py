import pathlib
from collections import defaultdict, deque

from rdflib import Graph, RDFS, RDF, OWL, URIRef, BNode


# Function to expand prefixed names
def expand_iri(iri, base_iri):
    """Expands prefixed names to full IRI using the base IRI."""
    print(iri)
    if isinstance(iri, URIRef):
        return iri  # Already a full IRI
    if base_iri and isinstance(iri, BNode):
        return URIRef(base_iri + iri[1:])  # Expand `:name` → `base_iri + name`
    if base_iri and isinstance(iri, str) and iri.startswith(":"):
        return URIRef(base_iri + iri[1:])
    return iri  # Otherwise, return as-is

# Function to extract the namespace (prefix) from a URI
def get_prefix(uri, g):
    """Extracts the prefix from a URI."""
    for prefix, namespace in g.namespaces():
        if uri.startswith(str(namespace)):
            return prefix
    return "unknown"  # Default if no known prefix

def main(ontology_path, is_owl=False):
    ontology_path = pathlib.Path(ontology_path)

    cls_type = RDFS.Class if not is_owl else OWL.Class
    prop_type = RDF.Property if not is_owl else OWL.ObjectProperty

    # Load the ontology
    g = Graph()
    g.parse(ontology_path, format="turtle")
    g.namespace_manager.bind("m4i", "http://w3id.org/nfdi4ing/metadata4ing#")

    # Extract the base IRI from the ontology (if defined)
    base_iri = None
    for prefix, namespace in g.namespaces():
        if prefix == "":  # Base IRI
            base_iri = str(namespace)
            break

    # Extract all classes and group by namespace
    classes_by_prefix = defaultdict(dict)  # {prefix: {URI: class_name}}
    for cls in g.subjects(RDF.type, cls_type):
        class_name = cls.split("#")[-1] if "#" in cls else cls.split("/")[-1]
        prefix = get_prefix(str(cls), g)  # Get the namespace prefix
        classes_by_prefix[prefix][cls] = class_name

    # Find subclass relationships (child -> parent mapping)
    subclass_mapping = defaultdict(dict)  # {prefix: {child_class: parent_class}}
    class_hierarchy = defaultdict(lambda: defaultdict(set))  # {prefix: {parent: {child}}}
    indegree = defaultdict(lambda: defaultdict(int))  # {prefix: {class: count}}

    for prefix, classes in classes_by_prefix.items():
        for cls in classes:
            parent = g.value(cls, RDFS.subClassOf)
            if parent in classes:
                subclass_mapping[prefix][cls] = parent
                class_hierarchy[prefix][parent].add(cls)
                indegree[prefix][cls] += 1  # Increment incoming edge count

    # Sort classes topologically within each prefix
    sorted_classes_by_prefix = defaultdict(list)
    for prefix, classes in classes_by_prefix.items():
        queue = deque([cls for cls in classes if indegree[prefix][cls] == 0])  # Start with root classes
        while queue:
            cls = queue.popleft()
            sorted_classes_by_prefix[prefix].append(cls)
            for child in class_hierarchy[prefix][cls]:
                indegree[prefix][child] -= 1
                if indegree[prefix][child] == 0:
                    queue.append(child)

    # Extract properties for each class
    class_definitions_by_prefix = defaultdict(dict)  # {prefix: {class: [properties]}}
    for prop in g.subjects(RDF.type, prop_type):
        domain = g.value(prop, RDFS.domain)
        range_ = g.value(prop, RDFS.range)

        prefix = get_prefix(str(domain), g)
        if domain in classes_by_prefix[prefix]:
            prop_name = prop.split("#")[-1] if "#" in prop else prop.split("/")[-1]
            prop_type = classes_by_prefix[prefix].get(range_, "str")  # Default to str if no explicit type

            if domain not in class_definitions_by_prefix[prefix]:
                class_definitions_by_prefix[prefix][domain] = []
            class_definitions_by_prefix[prefix][domain].append((prop_name, prop_type))

    # # Extract all classes and their names
    # classes = {}
    # for cls in g.subjects(RDF.type, cls_type):
    #     if not isinstance(cls, BNode):
    #         print(cls)
    #         # expanded_cls = expand_iri(cls, base_iri)
    #         class_name = cls.split("#")[-1] if "#" in cls else cls.split("/")[-1]
    #         classes[cls] = class_name

    # # Find subclass relationships (child -> parent mapping)
    # subclass_mapping = {}  # Maps child class -> parent class
    # class_hierarchy = defaultdict(set)  # Parent -> Set of Children (for sorting)
    # indegree = {cls: 0 for cls in classes}  # Count of incoming edges (for sorting)
    #
    # for cls in classes:
    #     parent = g.value(cls, RDFS.subClassOf)
    #     if parent in classes:
    #         subclass_mapping[cls] = parent
    #         class_hierarchy[parent].add(cls)
    #         indegree[cls] += 1  # Increment incoming edge count
    #
    # # Topological sorting (Kahn’s algorithm) to determine correct class order
    # sorted_classes = []
    # queue = deque([cls for cls in classes if indegree[cls] == 0])  # Start with root classes
    #
    # while queue:
    #     cls = queue.popleft()
    #     sorted_classes.append(cls)
    #
    #     for child in class_hierarchy[cls]:
    #         indegree[child] -= 1  # Remove dependency
    #         if indegree[child] == 0:
    #             queue.append(child)
    #
    # # Extract properties for each class
    # class_definitions = {}
    # for prop in g.subjects(RDF.type, prop_type):
    #     domain = g.value(prop, RDFS.domain)
    #     range_ = g.value(prop, RDFS.range)
    #
    #     if domain in classes:
    #         prop_name = prop.split("#")[-1] if "#" in prop else prop.split("/")[-1]
    #         prop_type = classes.get(range_, "str")  # Default to str if no explicit type
    #
    #         if domain not in class_definitions:
    #             class_definitions[domain] = []
    #         if prop_type in classes.values():
    #             class_definitions[domain].append(f"    {prop_name}: \"{prop_type}\"")
    #         else:
    #             class_definitions[domain].append(f"    {prop_name}: {prop_type}")

    # Generate Python models in sorted order
    # Create an output directory
    output_dir = ontology_path.parent / f"generated_models_from_{ontology_path.stem}"
    output_dir.mkdir(exist_ok=True, parents=True)

    all_classes = []
    for prefix, classes in classes_by_prefix.items():
        all_classes.extend(classes.values())
    # Generate separate Python files per prefix
    for prefix, sorted_classes in sorted_classes_by_prefix.items():
        output_file = output_dir / f"{prefix}_models.py"
        with open(output_file, "w") as f:
            f.write("from pydantic import BaseModel\n\n")

            for cls_uri in sorted_classes:
                class_name = classes_by_prefix[prefix][cls_uri]
                parent_class = classes_by_prefix[prefix].get(subclass_mapping[prefix].get(cls_uri), "BaseModel")

                f.write(f"class {class_name}({parent_class}):\n")
                if cls_uri in class_definitions_by_prefix[prefix]:
                    prop_defs = class_definitions_by_prefix[prefix][cls_uri]
                    for p in prop_defs:
                        if p[1] in all_classes:
                            f.write(f"    {p[0]}: \"{p[1]}\"\n")
                        else:
                            f.write(f"    {p[0]}: {p[1]}\n")
                    f.write("\n")
                else:
                    f.write("    pass\n\n")

        print(f"Generated: {output_file}")

    # output_file = pathlib.Path(ontology_path).parent / f"generated_{pathlib.Path(ontology_path).stem}.py"
    # with open(output_file, "w") as f:
    #     f.write("from pydantic import BaseModel\n\n")
    #
    #     for cls_uri in sorted_classes:
    #         class_name = classes[cls_uri]
    #         parent_class = classes.get(subclass_mapping.get(cls_uri), "BaseModel")  # Get parent class
    #         f.write(f"class {class_name}({parent_class}):\n")
    #         f.write(f"    # {cls_uri}\n")
    #         if cls_uri in class_definitions:
    #             f.write("\n".join(class_definitions[cls_uri]) + "\n\n")
    #         else:
    #             f.write("    pass\n\n")
    #
    # print(f"Python models generated in {output_file}")


if __name__ == "__main__":
    # ontology_path = "dcat3.ttl"  # Change this to your ontology file
    # ontology_path = "ssno.ttl"  # Change this to your ontology file
    # ontology_path = "m4i.ttl"  # Change this to your ontology file
    # ontology_path = "schemaorg.ttl"  # Change this to your ontology file
    # main(ontology_path, False)

    # ontology_path = "ssno.ttl"  # Change this to your ontology file
    # main(ontology_path, True)

    ontology_path = "m4i.ttl"  # Change this to your ontology file
    main(ontology_path, is_owl=True)


    ontology_path = "ssno.ttl"  # Change this to your ontology file
    main(ontology_path, is_owl=True)
