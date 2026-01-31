import os


def normalize_path(path: str) -> str:
    """
    Ensures:
    - No duplicate slashes
    - Consistent forward slashes
    - OS-independent output
    """
    if not path:
        return path

    normalized = os.path.normpath(path)
    return normalized.replace("\\", "/")
