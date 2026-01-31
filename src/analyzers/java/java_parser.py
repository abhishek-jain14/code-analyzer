from tree_sitter_languages import get_parser

_parser = get_parser("java")

def parse_file(path: str):
    with open(path, "rb") as f:
        source = f.read()
    tree = _parser.parse(source)
    return tree, source
