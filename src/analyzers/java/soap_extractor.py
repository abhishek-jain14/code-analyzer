from src.analyzers.java.java_parser import parse_file
from src.analyzers.java.java_symbols import find_nodes
from src.ir.models import EndpointIR


def _get_modifiers_text(node):
    """
    Tree-sitter Java does NOT expose modifiers as a field.
    They must be found by iterating children.
    """
    for child in node.children:
        if child.type == "modifiers":
            return child.text.decode(errors="ignore")
    return ""


def extract_soap_endpoints(java_files):
    print("\n>>> SOAP EXTRACTOR INVOKED")

    soap_endpoints = []

    for file_path in java_files:
        print(f"\n📄 FILE: {file_path}")

        try:
            raw_text = open(file_path, "r", encoding="utf-8", errors="ignore").read()
        except Exception as e:
            print("❌ Failed to read file:", e)
            continue

        if "@WebService" not in raw_text:
            print("⏭ No @WebService text found — skipping")
            continue

        tree, _ = parse_file(file_path)
        if not tree:
            print("❌ Parse failed")
            continue

        root = tree.root_node
        classes = find_nodes(root, "class_declaration")

        print("🏷 Classes found:", len(classes))

        for class_node in classes:
            name_node = class_node.child_by_field_name("name")
            class_name = name_node.text.decode() if name_node else "UnknownClass"

            print(f"\n🧩 CLASS: {class_name}")

            # ----------------------------------------
            # DEBUG: dump class children
            # ----------------------------------------
            print("📦 CLASS CHILDREN:")
            for i, c in enumerate(class_node.children):
                print(f"  [{i}] TYPE={c.type} TEXT={c.text.decode(errors='ignore')[:80]}")

            # ----------------------------------------
            # FIX: Detect @WebService via modifiers
            # ----------------------------------------
            class_modifiers_text = _get_modifiers_text(class_node)

            print("🔍 Class modifiers text:", class_modifiers_text)

            has_webservice = "@WebService" in class_modifiers_text
            print("✅ @WebService detected:", has_webservice)

            if not has_webservice:
                print("⏭ Skipping class (not SOAP)")
                continue

            # ----------------------------------------
            # Methods
            # ----------------------------------------
            methods = find_nodes(class_node, "method_declaration")
            print("🔧 Methods found:", len(methods))

            for method in methods:
                method_name_node = method.child_by_field_name("name")
                method_name = (
                    method_name_node.text.decode()
                    if method_name_node
                    else "unknown"
                )

                print(f"\n   ▶ METHOD: {method_name}")

                # DEBUG: method children
                for i, c in enumerate(method.children):
                    print(
                        f"      [{i}] TYPE={c.type} TEXT={c.text.decode(errors='ignore')[:80]}"
                    )

                method_modifiers_text = _get_modifiers_text(method)
                print("      🔍 Method modifiers text:", method_modifiers_text)

                has_webmethod = "@WebMethod" in method_modifiers_text
                print("      ✅ @WebMethod detected:", has_webmethod)

                if not has_webmethod:
                    print("      ⏭ Skipping method")
                    continue

                soap_endpoints.append(
                    EndpointIR(
                        protocol="SOAP",
                        service=class_name,
                        operation=method_name,
                        file=file_path,
                    )
                )

    print("\n>>> TOTAL SOAP ENDPOINTS FOUND:", len(soap_endpoints))
    return soap_endpoints
