import pathlib
from collections import defaultdict, deque

from rdflib import Graph, RDFS, RDF, OWL


# Function to extract the namespace (prefix) from a URI
def get_prefix(uri, g):
    """Extracts the prefix from a URI."""
    for prefix, namespace in g.namespaces():
        if uri.startswith(str(namespace)):
            return prefix
    return "unknown"  # Default if no known prefix


def generate(ontology_filename, is_owl=False):
    """This is still experimental and not yet fully functional!"""
    ontology_filename = pathlib.Path(ontology_filename)

    cls_type = RDFS.Class if not is_owl else OWL.Class
    prop_type = RDF.Property if not is_owl else OWL.ObjectProperty

    # Load the ontology
    g = Graph()
    g.parse(ontology_filename, format="turtle")
    g.namespace_manager.bind("m4i", "http://w3id.org/nfdi4ing/metadata4ing#")

    # Extract all classes and group by namespace
    classes_by_prefix = defaultdict(dict)  # {prefix: {URI: class_name}}
    for cls in g.subjects(RDF.type, cls_type):
        class_name = str(cls).split("#")[-1] if "#" in cls else str(cls).split("/")[-1]
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
            prop_name = str(prop).split("#")[-1] if "#" in prop else str(prop).split("/")[-1]
            prop_type = classes_by_prefix[prefix].get(range_, "str")  # Default to str if no explicit type

            if domain not in class_definitions_by_prefix[prefix]:
                class_definitions_by_prefix[prefix][domain] = []
            class_definitions_by_prefix[prefix][domain].append((prop_name, prop_type))

    # Generate Python models in sorted order
    # Create an output directory
    output_dir = ontology_filename.parent / f"generated_models_from_{ontology_filename.stem}"
    output_dir.mkdir(exist_ok=True, parents=True)

    all_classes = []
    for prefix, classes in classes_by_prefix.items():
        all_classes.extend(classes.values())
    # namespace_dict = dict(g.namespaces())

    # Generate separate Python files per prefix
    for prefix, sorted_classes in sorted_classes_by_prefix.items():
        if prefix != "unknown":
            output_file = output_dir / f"{prefix}.py"
            with open(output_file, "w") as f:
                f.write("from ontolutils import Thing, namespaces, urirefs\n")
                f.write("from pydantic import Field\n\n")

                for cls_uri in sorted_classes:
                    class_name = classes_by_prefix[prefix][cls_uri]
                    parent_class = classes_by_prefix[prefix].get(subclass_mapping[prefix].get(cls_uri), "Thing")

                    base_iri = str(cls_uri).split(class_name)[0]
                    f.write(f'@namespaces(schema="{base_iri}")\n')
                    f.write(f'@urirefs(\n')
                    f.write(f'    {class_name}="{prefix}:{class_name}",\n')
                    if cls_uri in class_definitions_by_prefix[prefix]:
                        prop_defs = class_definitions_by_prefix[prefix][cls_uri]
                        for p in prop_defs:
                            f.write(f'    {p[0]}="{prefix}:{p[0]}",\n')
                    f.write(f')\n')
                    f.write(f"class {class_name}({parent_class}):\n")
                    f.write(f'    """Pydantic Model for {prefix}:{class_name}"""\n')
                    if cls_uri in class_definitions_by_prefix[prefix]:
                        prop_defs = class_definitions_by_prefix[prefix][cls_uri]
                        for p in prop_defs:
                            if p[1] in all_classes:
                                f.write(f"    {p[0]}: \"{p[1]}\" = Field(default=None)\n")
                            else:
                                f.write(f"    {p[0]}: {p[1]} = Field(default=None)\n")
                        f.write("\n")
                    else:
                        f.write("    pass\n\n")

            print(f"Generated: {output_file}")


if __name__ == "__main__":
    ontology_path = "m4i.ttl"
    generate(ontology_path, is_owl=True)

    ontology_path = "ssno.ttl"
    generate(ontology_path, is_owl=True)

    ontology_path = "hdf5.ttl"
    generate(ontology_path, is_owl=True)
