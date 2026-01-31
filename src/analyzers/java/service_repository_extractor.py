import re
from pathlib import Path

def extract_service_repository_flows(java_files, repositories):
    print("\n>>> SERVICE → REPOSITORY EXTRACTOR INVOKED")
    print(f">>> Total Java files received: {len(java_files)}")

    flows = []

    # -----------------------------
    # Build repository name set
    # -----------------------------
    repo_names = set()
    for r in repositories:
        if isinstance(r, dict):
            repo_names.add(r.get("name"))
        else:
            repo_names.add(getattr(r, "name", None))

    print("\n>>> KNOWN REPOSITORIES")
    for r in repo_names:
        print("  -", r)

    if not repo_names:
        print("  ❌ NO repositories available — extractor will find NOTHING")

    # -----------------------------
    # Scan Java files
    # -----------------------------
    for file_path in java_files:
        file_path = Path(file_path)
        print("\n----------------------------------------")
        print("[SCAN FILE]", file_path)

        try:
            source = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print("  ❌ Failed to read file:", e)
            continue

        # -----------------------------
        # Detect service class
        # -----------------------------
        class_match = re.search(r"class\s+(\w+)", source)
        if not class_match:
            print("  ❌ No class found")
            continue

        class_name = class_match.group(1)
        print("  Class detected:", class_name)

        if not class_name.endswith("Service"):
            print("  ⏭️ Not a Service class — skipping")
            continue

        print("  ✅ Service class confirmed")

        # -----------------------------
        # Detect injected repositories
        # -----------------------------
        injected_repos = {}

        print("  🔍 Scanning for injected repositories...")

        # Field injection
        for repo in repo_names:
            if not repo:
                continue
            field_pattern = rf"{repo}\s+(\w+)\s*;"
            match = re.search(field_pattern, source)
            if match:
                var_name = match.group(1)
                injected_repos[var_name] = repo
                print(f"    ✅ Field injection found: {repo} → variable '{var_name}'")

        # Constructor injection
        constructor_match = re.search(
            rf"{class_name}\s*\(([^)]*)\)", source
        )
        if constructor_match:
            params = constructor_match.group(1)
            print("    Constructor parameters:", params)
            for repo in repo_names:
                if repo and repo in params:
                    param_match = re.search(rf"{repo}\s+(\w+)", params)
                    if param_match:
                        var_name = param_match.group(1)
                        injected_repos[var_name] = repo
                        print(f"    ✅ Constructor injection found: {repo} → '{var_name}'")

        if not injected_repos:
            print("  ❌ NO injected repositories detected in this service")

        # -----------------------------
        # Scan service methods
        # -----------------------------
        method_pattern = re.finditer(
            r"(public|protected|private)\s+\w+\s+(\w+)\s*\([^)]*\)\s*\{",
            source
        )

        for method in method_pattern:
            method_name = method.group(2)
            method_start = method.end()

            print(f"\n  ▶ Scanning method: {method_name}")

            method_body = source[method_start:]
            brace_count = 1
            i = 0
            while brace_count > 0 and i < len(method_body):
                if method_body[i] == "{":
                    brace_count += 1
                elif method_body[i] == "}":
                    brace_count -= 1
                i += 1

            method_body = method_body[:i]

            print("    Method body length:", len(method_body))

            for var_name, repo_name in injected_repos.items():
                call_pattern = rf"{var_name}\.(\w+)\s*\("
                calls = re.findall(call_pattern, method_body)

                if calls:
                    for repo_method in calls:
                        print(f"    ✅ Repository call found: {var_name}.{repo_method}()")
                        flows.append({
                            "service": class_name,
                            "service_method": method_name,
                            "repository": repo_name,
                            "repository_method": repo_method
                        })
                else:
                    print(f"    ❌ No calls found for repository variable '{var_name}'")

    print("\n>>> TOTAL SERVICE→REPOSITORY FLOWS:", len(flows))
    return flows
