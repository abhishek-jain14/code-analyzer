from src.core.config_loader import ROLE_CONFIG


def detect_role_by_path(file_path):
    path_lower = file_path.lower()

    for role, cfg in ROLE_CONFIG.items():
        for folder in cfg.get("folders", []):
            if f"/{folder}/" in path_lower or f"\\{folder}\\" in path_lower:
                return role
    return None


def detect_role_by_source(source_code):
    for role, cfg in ROLE_CONFIG.items():

        # Annotation-based
        for ann in cfg.get("annotations", []):
            if ann in source_code:
                return role

        # Interface inheritance (repositories)
        for iface in cfg.get("interfaces", []):
            if f"extends {iface}" in source_code:
                return role

    return None


def detect_role(file_path, source_code=None):
    """
    Unified role detection.
    - Path first (cheap)
    - Source second (accurate)
    """
    role = detect_role_by_path(file_path)
    if role:
        return role

    if source_code:
        role = detect_role_by_source(source_code)
        if role:
            return role

    return "unknown"


