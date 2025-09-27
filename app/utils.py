import re

def normalize(text: str) -> str:
    """Normalize text for consistent matching."""
    return text.strip().lower().replace('\n', ' ').replace('\r', '')

def normalize_operation(text: str) -> str:
    """Standardize operation terms across CCC and Mitchell estimates."""
    operation_map = {
        "remove / install": "r&i",
        "remove / replace": "repl",
        "remove and install": "r&i",
        "remove and replace": "repl",
        "repair": "rpr",
        "overhaul": "o/h",
        "adjust": "adj",
        "install": "inst"
    }
    norm = normalize(text)
    for raw, std in operation_map.items():
        norm = re.sub(rf"\b{re.escape(raw)}\b", std, norm)
    return norm

def normalize_orientation(text: str) -> str:
    """Standardize orientation terms across CCC and Mitchell estimates."""
    orientation_map = {
        "frt": "front",
        "r": "rt",
        "l": "lt",
        "rear": "rear"
    }
    norm = normalize(text)
    for raw, std in orientation_map.items():
        norm = re.sub(rf"\b{re.escape(raw)}\b", std, norm)
    return norm

def suggest_if_missing(lines: list, candidates: list, seen: set) -> list:
    """Suggest items from candidates that aren't already present in any line."""
    normalized_lines = [normalize(line) for line in lines]
    return [
        item for item in candidates
        if not any(normalize(item) in line for line in normalized_lines)
    ]