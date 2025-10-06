import re
from app.utils import normalize

# Repair-related verbs to detect valid operations
REPAIR_VERBS = [
    "rpr", "repl", "r&i", "blnd",
    "add for", "aim", "o/h", "adjust", "set", "calibrate", "deduct for overlap",
    "refn edges", "wheel alignment", "overlap major", "overlap minor", "clear coat"
]

def normalize_operation(text: str) -> str:
    text = normalize(text)

    # Collapse repeated verbs like "R&I R&I"
    for verb in REPAIR_VERBS:
        pattern = rf"\b({verb})\b\s+\1\b"
        text = re.sub(pattern, r"\1", text, flags=re.IGNORECASE)

    return text.strip()

def scan_repair_lines(lines: list[str]) -> list[str]:
    repair_lines = []
    verb_pattern = r"\b(" + "|".join(REPAIR_VERBS) + r")\b"
    skip_phrases = [
        "authorization", "Clear Coat Paint", "responsibility", "appraisal", "ACD", "NOTE:", "Adj.=", "Replace.", "Rpr=", "VIN=", "EPA=", "NHTSA="
    ]

    buffer = ""
    i = 0
    while i < len(lines):
        raw = lines[i].strip()
        if not raw or any(skip in raw for skip in skip_phrases):
            i += 1
            continue

        # If line is verb-only
        if re.search(verb_pattern, raw, flags=re.IGNORECASE) and len(raw.split()) == 1:
            buffer = raw
            i += 1
            continue

        # If buffer exists and current line is numeric, skip both
        if buffer and re.fullmatch(r"\d+(\.\d+)?", raw):
            buffer = ""
            i += 1
            continue

        # If buffer exists, combine with current line
        if buffer:
            combined = f"{buffer} {raw}"
            repair_lines.append(combined)
            buffer = ""
        elif re.search(verb_pattern, raw, flags=re.IGNORECASE):
            repair_lines.append(raw)

        i += 1

    return repair_lines