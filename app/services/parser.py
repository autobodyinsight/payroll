import re
from collections import defaultdict
from app.utils import normalize, normalize_operation

# Repair-related verbs to detect valid operations
REPAIR_VERBS = [
    "rpr", "repl", "r&i", "blnd", "repair", "replace", "remove", "install",
    "add for", "aim", "o/h", "adjust", "set", "calibrate"
]

# Patterns to skip irrelevant lines
SKIP_PATTERNS = [
    r"^\d{4} ",  # Year + vehicle line
    r"vin[:\s]",  # VIN lines
    r"license[:\s]",  # License plate
    r"^(owner|insured|adjuster|policy|claim|type|point|state|condition|job number|date of loss|odometer|color|transmission|radio|seats|wheels|decor|safety|other|paint|console|spoiler)",
    r"\d{1,2}/\d{1,2}/\d{4}",  # Dates
    r"\(\d{3}\)\s*\d{3}-\d{4}",  # Phone numbers
    r"^\d{5}$",  # Zip codes
    r"^\d{1,3}\s+[A-Z]{2,}$",  # Line numbers + all caps headers
]

def normalize_operation(text: str) -> str:
    text = normalize(text)
    for verb in REPAIR_VERBS:
        pattern = rf"\b({verb})\b\s+\1\b"
        text = re.sub(pattern, r"\1", text)
    return text.strip()

def extract_description(line: str) -> str:
    line = re.sub(r"^\d+\s*", "", line)  # Remove line numbers
    line = re.sub(r"\b[A-Z0-9]{6,}\b", "", line)  # Remove part numbers
    line = re.sub(r"\b\d{1,5}(\.\d{1,2})?\b", "", line)  # Remove prices/quantities
    line = re.sub(r"\bIncl\b", "", line, flags=re.IGNORECASE)

    # Remove leading repair verbs
    verbs_pattern = r"^(?:" + "|".join(REPAIR_VERBS) + r")\b\s*"
    line = re.sub(verbs_pattern, "", line, flags=re.IGNORECASE)

    line = re.sub(r"[^a-zA-Z0-9\s\-&/]", "", line)
    return line.strip().title()

def parse_pdf_lines(lines: list[str]) -> dict:
    grouped = {"body": [], "paint": []}

    for i, line in enumerate(lines):
        norm = normalize(line)
        norm = normalize_operation(norm)

        if not norm or norm in ["*", "<>", "—"]:
            continue
        if any(re.search(pat, norm) for pat in SKIP_PATTERNS):
            continue
        if "total cost" in norm or "net cost" in norm:
            continue

        match = re.search(r"(\d+(\.\d+)?)(\s+(\d+(\.\d+)?))?$", norm)
        if not match:
            continue

        has_verb = any(verb in norm for verb in REPAIR_VERBS)
        if not has_verb and float(match.group(1)) > 10:
            continue

        description = extract_description(line)

        try:
            labor_time = float(match.group(1))
            if labor_time > 10:
                continue

            entry = {
                "operation": description,
                "labor_time": labor_time,
                "category": "body"
            }

            if "blnd" in norm or "blend" in norm:
                entry["category"] = "paint"
                grouped["paint"].append(entry)
            else:
                grouped["body"].append(entry)

            if match.group(4):
                paint_time = float(match.group(4))
                if paint_time > 10:
                    continue

                grouped["paint"].append({
                    "operation": description,
                    "labor_time": paint_time,
                    "category": "paint"
                })

        except ValueError:
            print(f"[ERROR] Could not parse labor/paint from line: {norm}")
            continue

    return grouped

def format_results_as_lines(grouped: dict) -> str:
    lines = []
    total_body = 0.0
    total_paint = 0.0

    for item in grouped.get("body", []):
        lines.append(f"{item['operation']}, {item['labor_time']}, {item['category']}")
        total_body += item["labor_time"]

    for item in grouped.get("paint", []):
        lines.append(f"{item['operation']}, {item['labor_time']}, {item['category']}")
        total_paint += item["labor_time"]

    lines.append("")
    lines.append(f"Total Body Labor: {total_body}")
    lines.append(f"Total Paint Labor: {total_paint}")

    return "\n".join(lines)