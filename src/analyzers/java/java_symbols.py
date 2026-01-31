from tree_sitter_languages import get_parser
from tree_sitter import Parser




# =========================================================
# Parser
# =========================================================

def parse_java_file(file_path):
    """
    Parse a Java source file and return (tree, source_code).
    """

    parser = get_parser("java")

    with open(file_path, "rb") as f:
        source_bytes = f.read()

    tree = parser.parse(source_bytes)
    source_code = source_bytes
    return tree, source_code


# =========================================================
# AST Utilities
# =========================================================

def find_nodes(node, node_type):
    """
    Recursively find all nodes of a given type.
    """
    results = []

    if node.type == node_type:
        results.append(node)

    for child in node.children:
        results.extend(find_nodes(child, node_type))

    return results


def get_node_text(node, source):
    """
    Returns source text for a syntax node.
    Works whether source is bytes or str.
    """

    text = source[node.start_byte: node.end_byte]

    if isinstance(text, bytes):
        return text.decode("utf-8", errors="ignore")

    return text

def extract_annotation_value(node):
    """
    Recursively extract string literal from a Java annotation AST node.

    Supports:
      @GetMapping("/x")
      @PostMapping("/x/{id}")
      @RequestMapping(value="/x")
      @RequestMapping(path="/x")
    """
    if node.type == "string_literal":
        return node.text.decode().strip('"')

    for child in node.children:
        value = extract_annotation_value(child)
        if value:
            return value

    return ""