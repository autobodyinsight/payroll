import re
from collections import defaultdict
from app.utils import normalize, normalize_operation

REPAIR_VERBS = [
    "rpr", "repl", "r&i", "blnd", "repair", "replace", "remove", "install",
    "add for", "aim", "o/h", "adjust", "set", "calibrate"
]

SKIP_PATTERNS = [
    r"^\d{4} ",                  # Year + vehicle line
    r"vin[:\s]",                 # VIN lines
    r"license[:\s]",            # License plate
    r"^(owner|insured|adjuster|policy|claim|type|point|state|condition|job number|date of loss|odometer|color|transmission|radio|seats|wheels|decor|safety|other|paint|console|spoiler)",  # headers
    r"\d{1,2}/\d{1,2}/\d{4}",    # Dates
    r"\(\d{3}\)\s*\d{3}-\d{4}",  # Phone numbers
    r"^\d{5}$",                  # Zip codes
    r"^\d{1,3}\s+[A-Z]{2,}$",    # Line numbers + all caps headers
]

def extract_description(line: str) -> str:
    # Remove leading line numbers
    line = re.sub(r"^\d+\s*", "", line)

    # Remove part numbers (6+ alphanumeric), quantities, prices, and 'Incl'
    line = re.sub(r"\b[A-Z0-9]{6,}\b", "", line)  # part numbers
    line = re.sub(r"\b\d{1,5}(\.\d{1,2})?\b", "", line)  # prices/quantities
    line = re.sub(r"\bIncl\b", "", line, flags=re.IGNORECASE)

    # Clean up and title-case
    line = re.sub(r"[^a-zA-Z0-9\s\-&/]", "", line)
    return line.strip().title()

def parse_pdf_lines(lines: list[str]) -> dict:
    grouped = {"body": [], "paint": []}

    for i, line in enumerate(lines):
        norm = normalize(line)
        norm = normalize_operation(norm)

        # Skip junk lines
        if not norm or norm in ["*", "<>", "—"]:
            continue
        if any(re.search(pat, norm) for pat in SKIP_PATTERNS):
            continue
        if "total cost" in norm or "net cost" in norm:
            continue

        # Must contain at least one numeric value (labor or paint)
        match = re.search(r"(\d+(\.\d+)?)(\s+(\d+(\.\d+)?))?$", norm)
        if not match:
            continue

        # Must contain a repair verb or fallback to labor-only if valid
        has_verb = any(verb in norm for verb in REPAIR_VERBS)
        if not has_verb and float(match.group(1)) > 10:
            continue  # likely a price, not labor

        description = extract_description(line)

        try:
            labor_time = float(match.group(1))
            if labor_time > 10:
                continue  # skip price overmatch

            grouped["body"].append({
                "operation": description,
                "labor_time": labor_time,
                "category": "body"
            })

            if match.group(4):
                paint_time = float(match.group(4))
                if paint_time > 10:
                    continue  # skip price overmatch

                grouped["paint"].append({
                    "operation": description,
                    "labor_time": paint_time,
                    "category": "paint"
                })

        except ValueError:
            print(f"[ERROR] Could not parse labor/paint from line: {norm}")
            continue

    return grouped