from src.analyzers.java.java_symbols import (
    parse_java_file,
    find_nodes,
    get_node_text,
)
from src.analyzers.java.role_detector import detect_role


def extract_repository_queries(java_files):
    """
    Returns:
    {
      ("UserRepository", "getUserByStatus"): "select u from User u where u.status = ?1"
    }
    """
    repo_queries = {}

    for file_path in java_files:
        if "repository" not in file_path.lower():
            continue

        tree, source_code = parse_java_file(file_path)
        root = tree.root_node

        repo_name = get_repository_name(root, source_code)
        if not repo_name:
            continue

        methods = find_nodes(root, "method_declaration")

        for method in methods:
            method_name = get_method_name(method, source_code)
            query = extract_query_annotation(method, source_code)

            if query:
                repo_queries[(repo_name, method_name)] = query
                print(
                    f"🧠 REPO QUERY: {repo_name}.{method_name} → {query}"
                )

    return repo_queries


# ---------------- HELPERS ---------------- #

def get_repository_name(root, source_code):
    classes = find_nodes(root, "class_declaration")
    if not classes:
        return None
    name_node = classes[0].child_by_field_name("name")
    return get_node_text(name_node, source_code)


def get_method_name(method_node, source_code):
    name_node = method_node.child_by_field_name("name")
    if not name_node:
        return None
    return get_node_text(name_node, source_code)


def extract_query_annotation(method_node, source_code):
    annotations = find_nodes(method_node, "annotation")

    for ann in annotations:
        text = get_node_text(ann, source_code)
        if "@Query" in text and "(" in text:
            return (
                text.split("(", 1)[1]
                .rsplit(")", 1)[0]
                .replace("\"", "")
                .strip()
            )

    return None
