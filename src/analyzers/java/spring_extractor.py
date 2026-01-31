from src.analyzers.java.java_parser import parse_file
from src.analyzers.java.java_symbols import (
    find_nodes,
    extract_annotation_value,
)
from src.frameworks.spring.annotations import REST_MAPPINGS
from src.ir.models import EndpointIR


def extract_spring_endpoints(java_files):
    """
    Extract Spring REST endpoints from a list of Java source files.
    Returns a list of EndpointIR objects.
    """
    endpoints = []

    for file_path in java_files:
        tree, source_code = parse_file(file_path)
        if not tree:
            continue

        root = tree.root_node

        # Iterate over classes
        for class_node in find_nodes(root, "class_declaration"):
            base_path = ""

            # ✅ Extract controller class name
            class_name_node = class_node.child_by_field_name("name")
            if not class_name_node:
                continue

            controller_name = class_name_node.text.decode()

            # ---- Class-level @RequestMapping ----
            for ann in find_nodes(class_node, "annotation"):
                name_node = ann.child_by_field_name("name")
                if not name_node:
                    continue

                ann_name = name_node.text.decode()
                if ann_name == "RequestMapping":
                    base_path = extract_annotation_value(ann) or ""

            # Iterate over methods
            for method in find_nodes(class_node, "method_declaration"):
                method_name_node = method.child_by_field_name("name")
                if not method_name_node:
                    continue

                handler = method_name_node.text.decode()

                # Look for Spring REST annotations
                for ann in find_nodes(method, "annotation"):
                    name_node = ann.child_by_field_name("name")
                    if not name_node:
                        continue

                    ann_name = name_node.text.decode()

                    if ann_name in REST_MAPPINGS:
                        http_method = REST_MAPPINGS[ann_name]

                        # Method-level path
                        method_path = extract_annotation_value(ann) or ""

                        # Merge class + method paths
                        full_path = (base_path + method_path).replace("//", "/")
                        if not full_path.startswith("/"):
                            full_path = "/" + full_path

                        endpoints.append(
                            EndpointIR(
                                http_method=http_method,
                                path=full_path,
                                handler=handler,              # method name
                                service=controller_name,      # controller class
                                file=file_path,
                                protocol="REST"
                            )
                        )

    return endpoints
