import re


# ==================================================
# PATTERNS
# ==================================================

# if (condition) { throw new ExceptionType(...); }
IF_THROW_PATTERN = re.compile(
    r"if\s*\((?P<condition>.*?)\)\s*\{.*?throw\s+new\s+(?P<exception>\w+)",
    re.DOTALL
)

# validateUser(), userValidation.validateUser(), checkX(), isValidX()
VALIDATION_CALL_PATTERN = re.compile(
    r"(?:\w+\.)?(validate\w+|check\w+|isValid\w*)\s*\(",
    re.IGNORECASE
)

METHOD_HEADER_PATTERN = re.compile(
    r"(public|protected|private)\s+[\w<>]+\s+(\w+)\s*\([^)]*\)\s*\{"
)


# ==================================================
# BUILD GLOBAL METHOD INDEX (ONCE)
# ==================================================

def build_method_index(java_files):
    """
    Builds an index:
    {
        method_name: [
            {
                "class": class_name,
                "body": method_body
            }
        ]
    }
    """
    index = {}

    for file_path in java_files:
        if not file_path.endswith(".java"):
            continue

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source = f.read()
        except:
            continue

        class_match = re.search(r"class\s+(\w+)", source)
        if not class_match:
            continue

        class_name = class_match.group(1)

        for match in METHOD_HEADER_PATTERN.finditer(source):
            method_name = match.group(2)
            start = match.end()

            brace_count = 1
            i = start

            while i < len(source) and brace_count > 0:
                if source[i] == "{":
                    brace_count += 1
                elif source[i] == "}":
                    brace_count -= 1
                i += 1

            body = source[start:i - 1]

            index.setdefault(method_name, []).append({
                "class": class_name,
                "body": body
            })

    return index


# ==================================================
# SERVICE VALIDATION EXTRACTOR
# ==================================================

def extract_service_validations(java_files):
    print("\n>>> SERVICE VALIDATION EXTRACTOR INVOKED")

    validations = []

    # Build method index once
    method_index = build_method_index(java_files)

    for file_path in java_files:
        path = file_path.replace("\\", "/")
        if "/services/" not in path or not path.endswith(".java"):
            continue

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source = f.read()
        except Exception as e:
            print(f"[ERROR] Cannot read {file_path}: {e}")
            continue

        class_match = re.search(r"class\s+(\w+)", source)
        if not class_match:
            continue

        service_name = class_match.group(1)
        print(f"\n[SCAN SERVICE] {service_name}")

        method_headers = list(METHOD_HEADER_PATTERN.finditer(source))

        if not method_headers:
            print("  ❌ No methods detected")
            continue

        print(f"  ▶ Methods detected: {len(method_headers)}")

        # --------------------------------------------------
        # Scan each service method
        # --------------------------------------------------
        for header in method_headers:
            method_name = header.group(2)
            start_index = header.end()

            brace_count = 1
            i = start_index

            while i < len(source) and brace_count > 0:
                if source[i] == "{":
                    brace_count += 1
                elif source[i] == "}":
                    brace_count -= 1
                i += 1

            body = source[start_index:i - 1]

            print(f"\n  ▶ Scanning method: {method_name}")

            # ----------------------------------------------
            # 1️⃣ Inline IF + THROW validations
            # ----------------------------------------------
            for match in IF_THROW_PATTERN.finditer(body):
                validations.append({
                    "type": "if_throw",
                    "service": service_name,
                    "method": method_name,
                    "condition": match.group("condition").strip(),
                    "exception": match.group("exception").strip()
                })

            # ----------------------------------------------
            # 2️⃣ Validation method calls (expand them)
            # ----------------------------------------------
            for call in VALIDATION_CALL_PATTERN.finditer(body):
                validation_method = call.group(1)

                validation_entry = {
                    "type": "method_call",
                    "service": service_name,
                    "method": method_name,
                    "validation_method": validation_method,
                    "validations": []
                }

                targets = method_index.get(validation_method, [])

                for target in targets:
                    for im in IF_THROW_PATTERN.finditer(target["body"]):
                        validation_entry["validations"].append({
                            "class": target["class"],
                            "condition": im.group("condition").strip(),
                            "exception": im.group("exception").strip()
                        })

                validations.append(validation_entry)

    print("\n>>> TOTAL SERVICE VALIDATIONS:", len(validations))
    return validations
