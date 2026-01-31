import re
from pathlib import Path

def extract_repositories(java_files):
    print("\n>>> REPOSITORY EXTRACTOR INVOKED")
    repositories = []

    for file_path in java_files:
        path = Path(file_path)

        # ✅ folder heuristic (repository OR repositories)
        folder_hit = any(
            part.lower().startswith("repo")
            for part in path.parts
        )

        if not folder_hit:
            continue

        if not path.name.endswith(".java"):
            continue

        source = path.read_text(encoding="utf-8", errors="ignore")

        # ✅ class detection (ANY class, not only *Repository)
        match = re.search(r"public\s+class\s+(\w+)", source)
        if not match:
            continue

        class_name = match.group(1)

        print(f"[REPOSITORY FOUND] {class_name} → {file_path}")

        repositories.append({
            "name": class_name,
            "file": file_path
        })

    print(f">>> TOTAL REPOSITORIES FOUND: {len(repositories)}")
    return repositories
