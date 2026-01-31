from tree_sitter_languages import get_parser

def get_language_parser(language: str):
    if language == "java":
        return get_parser("java")
    raise ValueError(f"Unsupported language: {language}")
