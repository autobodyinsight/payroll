import re
from collections import defaultdict

CATEGORY_RULES = {
    "body": ["replace", "repair", "install", "remove", "adjust", "rpr", "r&i", "bumper", "grille", "valance", "bracket"],
    "refinish": ["refinish", "paint", "sand", "prime", "clearcoat"]
}

def parse_estimate(text: str):
    lines = text.splitlines()
    grouped = defaultdict(list)

    for line in lines:
        if not line.strip():
            continue

        description = extract_description(line)
        labor_time, paint_time = extract_labor_and_paint(line)

        if labor_time is not None:
            grouped["body"].append({
                "operation": description,
                "labor_time": labor_time,
                "category": "body"
            })

        if paint_time is not None:
            grouped["paint"].append({
                "operation": description,
                "labor_time": paint_time,
                "category": "paint"
            })

    return dict(grouped)

def extract_labor_and_paint(line: str):
    # Match two float numbers in the line (labor and paint)
    matches = re.findall(r"\b(\d+(\.\d+)?)\b", line)
    if len(matches) >= 2:
        return float(matches[0][0]), float(matches[1][0])
    elif len(matches) == 1:
        return float(matches[0][0]), None
    else:
        return None, None

def extract_description(line: str):
    # Try to extract description from structured line
    parts = re.split(r"\s{2,}", line.strip())
    if len(parts) >= 3:
        return parts[2]  # Assuming description is third column
    return line.strip()