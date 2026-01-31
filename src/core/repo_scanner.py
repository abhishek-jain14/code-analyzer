import os


def scan_repo(repo_path, extensions=None):
    """
    Recursively scan repository and return files
    matching given extensions.
    """
    if extensions is None:
        extensions = [".java"]

    matched_files = []

    for root, _, files in os.walk(repo_path):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                matched_files.append(os.path.join(root, file))

    return matched_files