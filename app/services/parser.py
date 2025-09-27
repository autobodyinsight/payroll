import re
from collections import defaultdict

# Define known repair verbs and categories
REPAIR_VERBS = ["rpr", "repl", "rt&i", "r&i", "o/h", "adj", "inst"]
CATEGORY_RULES = {
    "body": ["bumper", "grille", "valance", "cover", "hole", "panel", "lamp", "bracket"],
    "paint": ["clear coat", "refinish", "paint", "prime", "sand"]
}

def parse_estimate(text: str):
    lines = text.splitlines()
    grouped = defaultdict(list)

    for i, line in enumerate(lines):
        line_clean = line.strip().lower()
        print(f"[REARBODY REPL RULE] Scanning line: {i+1} {line_clean}")

        if not any(verb in line_clean for verb in REPAIR_VERBS):
            continue  # Skip lines without repair verbs

        # Extract labor and paint hours
        hours = re.findall(r"\d+(\.\d+)?", line_clean)
        if not hours:
            continue

        description = extract_description(line_clean)
        category = classify_category(description)

        # Assign hours: first is labor, second is paint (if present)
        if len(hours) >= 1:
            grouped["body"].append({
                "operation": description,
                "labor_time": float(hours[0]),
                "category": "body"
            })
        if len(hours) >= 2:
            grouped["paint"].append({
                "operation": description,
                "labor_time": float(hours[1]),
                "category": "paint"
            })

    return dict(grouped)

def extract_description(line: str):
    # Remove symbols and trailing numbers
    line = re.sub(r"[^a-zA-Z0-9\s\-&]", "", line)
    line = re.sub(r"\d+(\.\d+)?", "", line)
    return line.strip().title()

def classify_category(description: str):
    desc_lower = description.lower()
    for category, keywords in CATEGORY_RULES.items():
        if any(kw in desc_lower for kw in keywords):
            return category
    return "body"  # Default to body if unknown