import os
import re

from src.analyzers.java.role_detector import detect_role

def extract_entities(java_files):
    print("\n>>> ENTITY EXTRACTOR INVOKED")

    entities = []

    for file_path in java_files:

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        role = detect_role(file_path, source)
        if role != "entity":
            continue

        if "@Entity" not in source:
            continue

        name = None
        table = None

        for line in source.splitlines():
            line = line.strip()

            if line.startswith("public class"):
                name = line.split()[2]

            if "@Table" in line and "name" in line:
                table = line.split("name")[1].split('"')[1]

        if name:
            entities.append({
                "name": name,
                "file": file_path,
                "table": table,
            })
            print(f"[ENTITY FOUND] {name} → {table}")

    print(f">>> TOTAL ENTITIES FOUND: {len(entities)}")
    return entities

ENTITY_FIELD_PATTERN = re.compile(
    r"(private|protected|public)\s+([\w<>]+)\s+(\w+)\s*;",
    re.MULTILINE
)

FIELD_PATTERN = re.compile(
    r"(private|protected|public)\s+([\w<>]+)\s+(\w+)\s*;",
    re.MULTILINE
)

COLUMN_PATTERN = re.compile(
    r"@Column\s*\(\s*name\s*=\s*\"([^\"]+)\"",
    re.MULTILINE
)


def extract_entity_fields(entities):
    entity_field_index = {}

    for entity in entities:
        entity_name = entity["name"]
        file_path = entity["file"]

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source = f.read()
        except Exception as e:
            print(f"[ERROR] Cannot read entity file {file_path}: {e}")
            continue

        fields = []
        last_column = None

        lines = source.splitlines()

        for line in lines:
            column_match = COLUMN_PATTERN.search(line)
            if column_match:
                last_column = column_match.group(1)
                continue

            field_match = FIELD_PATTERN.search(line)
            if field_match:
                fields.append({
                    "field_name": field_match.group(3),
                    "field_type": field_match.group(2),
                    "db_column_name": last_column or field_match.group(3)
                })
                last_column = None

        entity_field_index[entity_name] = fields

    return entity_field_index
