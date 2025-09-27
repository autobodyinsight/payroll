import re

CATEGORY_RULES = {
    "body": ["replace", "repair", "install", "remove", "adjust"],
    "refinish": ["refinish", "paint", "sand", "prime", "clearcoat"],
    "mechanical": ["diagnose", "align", "calibrate", "scan", "reset"]
}

def parse_estimate(text: str):
    lines = text.splitlines()
    parsed = []
    for line in lines:
        labor_time = extract_labor_time(line)
        category = classify_category(line)
        if labor_time and category:
            parsed.append({
                "operation": line.strip(),
                "labor_time": labor_time,
                "category": category
            })
    return parsed

def extract_labor_time(line: str):
    match = re.search(r"(\d+(\.\d+)?)\s*(hrs?|hours?)", line.lower())
    return float(match.group(1)) if match else None

def classify_category(line: str):
    line_lower = line.lower()
    for category, keywords in CATEGORY_RULES.items():
        if any(kw in line_lower for kw in keywords):
            return category.capitalize()
    return None