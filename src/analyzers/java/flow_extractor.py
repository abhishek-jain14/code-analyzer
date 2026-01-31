from src.analyzers.java.java_symbols import (
    parse_java_file,
    find_nodes,
    get_node_text,
)
from src.ir.models import ControllerServiceFlowIR
from src.analyzers.java.role_detector import detect_role


def extract_controller_service_flows(java_files, controller_inputs):
    flows = []

    print(">>> FLOW EXTRACTOR INVOKED")
    print(">>> Total Java files received:", len(java_files))

    for file_path in java_files:
        
        tree, source_code = parse_java_file(file_path)
        root = tree.root_node

        if isinstance(source_code, bytes):
            source_code = source_code.decode("utf-8", errors="ignore")
            
        role = detect_role(file_path, source_code)
        if role != "controller":
            print("  - SKIP (not a controller)", file_path)
            continue

        print("\n[CONTROLLER FILE]", file_path)

        controller_class = get_class_name(root, source_code)

        # ✅ FIX 1: extract class-level base path
        base_path = extract_controller_base_path(root, source_code)
        print(f"  Controller base path: {base_path}")

        service_fields = extract_service_fields(root, source_code)
        methods = find_nodes(root, "method_declaration")

        for method in methods:
            controller_method = get_method_name(method, source_code)
            http_method, method_path = extract_endpoint_signature(
                method, source_code
            )

            # Skip methods without mappings
            if http_method == "UNKNOWN":
                continue

            # ✅ FIX 2: combine base path + method path
            full_path = normalize_path(base_path, method_path)

            service_calls = find_service_calls(
                method, source_code, service_fields
            )

            for service_name, service_method in service_calls:
                flow = ControllerServiceFlowIR(
                    endpoint=f"{http_method} {full_path}",
                    controller=f"{controller_class}.{controller_method}",
                    service=service_name,
                    service_method=service_method,
                    http_method=http_method,
                    path=full_path
                )

                # ===== Attach controller inputs =====
                flow_key = f"{controller_class}.{controller_method}"
                flow.inputs = controller_inputs.get(flow_key, [])
                # ===========================================

                print(
                    f"  ✅ FLOW: {http_method} {full_path} → "
                    f"{service_name}.{service_method}"
                )

                flows.append(flow)

    print(f">>> TOTAL CONTROLLER→SERVICE FLOWS: {len(flows)}")
    return flows


# ---------------- HELPERS ---------------- #

def get_class_name(root, source_code):
    classes = find_nodes(root, "class_declaration")
    if not classes:
        return "UnknownController"
    name_node = classes[0].child_by_field_name("name")
    return get_node_text(name_node, source_code)


def extract_controller_base_path(root, source_code):
    """
    Extracts class-level @RequestMapping path
    Example:
      @RequestMapping("/api/user")
    """
    annotations = find_nodes(root, "annotation")

    for ann in annotations:
        text = get_node_text(ann, source_code)
        if "RequestMapping" in text and "(" in text:
            return (
                text.split("(", 1)[1]
                .replace(")", "")
                .replace("\"", "")
                .strip()
            )

    return ""


def normalize_path(base_path, method_path):
    """
    Safely joins class-level and method-level paths
    """
    if not base_path:
        return method_path

    if not method_path:
        return base_path

    return f"{base_path.rstrip('/')}/{method_path.lstrip('/')}"


def extract_service_fields(root, source_code):
    services = {}

    # @Autowired fields
    fields = find_nodes(root, "field_declaration")
    for field in fields:
        text = get_node_text(field, source_code)
        if "@Autowired" in text:
            parts = text.replace(";", "").split()
            if len(parts) >= 2:
                services[parts[-1]] = parts[-2]

    # Constructor injection
    ctors = find_nodes(root, "constructor_declaration")
    for ctor in ctors:
        params = find_nodes(ctor, "formal_parameter")
        for p in params:
            text = get_node_text(p, source_code)
            parts = text.split()
            if len(parts) == 2:
                services[parts[1]] = parts[0]

    print("  Injected services:", services)
    return services


def find_service_calls(method_node, source_code, service_fields):
    calls = []

    invocations = find_nodes(method_node, "method_invocation")
    for inv in invocations:
        text = get_node_text(inv, source_code)

        if "." not in text:
            continue

        obj, rest = text.split(".", 1)
        method = rest.split("(")[0]

        if obj in service_fields:
            calls.append((service_fields[obj], method))

    return calls


def get_method_name(method_node, source_code):
    name_node = method_node.child_by_field_name("name")
    if not name_node:
        return "unknown"
    return get_node_text(name_node, source_code)


def extract_endpoint_signature(method_node, source_code):
    """
    Returns:
      ("GET", "/list")
    """
    annotations = find_nodes(method_node, "annotation")
    http = "UNKNOWN"
    path = ""

    for ann in annotations:
        text = get_node_text(ann, source_code)

        if "GetMapping" in text:
            http = "GET"
        elif "PostMapping" in text:
            http = "POST"
        elif "PutMapping" in text:
            http = "PUT"
        elif "DeleteMapping" in text:
            http = "DELETE"

        if "(" in text:
            path = (
                text.split("(", 1)[1]
                .replace(")", "")
                .replace("\"", "")
                .strip()
            )

    return http, path
