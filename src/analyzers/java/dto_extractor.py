import re

from src.analyzers.java.role_detector import detect_role

CONTROLLER_PARAM_PATTERN = re.compile(
    r"@(?P<annotation>RequestBody|RequestParam|PathVariable)\s+"
    r"(?:\w+\s+)?(?P<type>\w+)\s+(?P<name>\w+)"
)

PRIMITIVES = {
    "int", "long", "float", "double", "boolean", "char", "byte", "short"
    "Integer", "Long", "Float", "Double", "Boolean", "Character", "Byte", "Short",
    "String"
}

def extract_controller_inputs(java_files):
    controller_inputs = {}

    for file_path in java_files:

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        if detect_role(file_path.replace("\\", "/"), source) != "controller":    
            continue

        class_match = re.search(r"class\s+(\w+)", source)
        if not class_match:
            continue

        controller = class_match.group(1)

        for method_match in re.finditer(
            r"(public|protected)\s+[\w<>]+\s+(\w+)\s*\(([^)]*)\)",
            source
        ):
            method = method_match.group(2)
            signature = method_match.group(3)

            key = f"{controller}.{method}"
            #flow["inputs"] = flow.get(key, [])
            controller_inputs[key] = []

            for param in CONTROLLER_PARAM_PATTERN.finditer(signature):
                annotation = param.group("annotation")
                param_type = param.group("type")
                param_name = param.group("name")

                source_type = {
                    "RequestBody": "RequestBody",
                    "RequestParam": "RequestParam",
                    "PathVariable": "PathVariable"
                }[annotation]

                controller_inputs[key].append({
                    "name": param_name,
                    "type": param_type,
                    "source": source_type
                })

    return controller_inputs

DTO_FIELD_PATTERN = re.compile(
    r"(private|protected|public)\s+([\w<>]+)\s+(\w+)\s*;",
    re.MULTILINE
)

def extract_input_object_fields(java_files, inputs):
    input_objects = {}

    object_types = {
        param["type"]
        for method_inputs in inputs.values()
        for param in method_inputs
        if param["type"] not in PRIMITIVES
    }


    for file_path in java_files:
        if not file_path.endswith(".java"):
            continue

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        role = detect_role(file_path, source)
        print("********************* dto file_path: ", file_path, " role:", role)
        if role != "dto" and role != "entity":
            continue
            
        class_match = re.search(r"class\s+(\w+)", source)
        if not class_match:
            continue

        class_name = class_match.group(1)

        if class_name not in object_types:
            continue

        fields = []
        for match in DTO_FIELD_PATTERN.finditer(source):
            fields.append({
                "field": match.group(3),
                "type": match.group(2)
            })

        input_objects[class_name] = {
            "fields": fields
        }

    return input_objects



