from src.analyzers.java.java_symbols import (
    parse_java_file,
    find_nodes,
    get_node_text,
)
from src.ir.models import ServiceFlowIR
from src.analyzers.java.role_detector import detect_role


def extract_service_flows(java_files):
    print("\n>>> Service extractor invoked")
    print(">>> Total Java files received:", len(java_files))

    flows = []

    for file_path in java_files:
        print("\n[CHECK FILE]", file_path)
        try:
            tree, source = parse_java_file(file_path)
        except Exception as e:
            print("  - PARSE ERROR:", e)
            continue

        if isinstance(source, bytes):
            source = source.decode("utf-8", errors="ignore")

        role = detect_role(file_path, source)
        if role != "service":
            print("  - SKIP (not a service)", file_path)
            continue

        print("  - Candidate service file")

        
        root = tree.root_node
        print("  - Parsed successfully")

        classes = find_nodes(root, "class_declaration")
        print("  - Classes found:", len(classes))

        for cls in classes:
            class_name_node = cls.child_by_field_name("name")
            if not class_name_node:
                print("    - Class without name (skip)")
                continue

            class_name = get_node_text(class_name_node, source)
            print("    - Class:", class_name)

            if detect_role(file_path, source) not in ["service"]:
                print("      - SKIP (not *Service)")
                continue

            print("      - VALID SERVICE CLASS")

            methods = find_nodes(cls, "method_declaration")
            print("      - Methods found:", len(methods))

            for method in methods:
                method_name_node = method.child_by_field_name("name")
                if not method_name_node:
                    print("        - Method without name (skip)")
                    continue

                method_name = get_node_text(method_name_node, source)
                print("        - Method:", method_name)

                flows.append(
                    ServiceFlowIR(
                        service=class_name,
                        method=method_name,
                        file=file_path
                    )
                )

    print("\n>>> Total service flows extracted:", len(flows))
    return flows
