import re
from app.utils import normalize

# Repair-related verbs to detect valid operations
REPAIR_VERBS = [
    "rpr", "repl", "r&i", "blnd", "refn",
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
    seen_supplement_lines = set()

    verb_pattern = r"\b(" + "|".join(REPAIR_VERBS) + r")\b"
    skip_phrases = [
        "authorization", "Clear Coat Paint", "responsibility", "manufactured",
        "appraisal", "ACD", "NOTE:", "Adj.=", "Replace.", "Rpr=", "VIN=", "EPA=", "NHTSA=",
        "freight", "FREIGHT"
    ]

    buffer = ""
    i = 0
    while i < len(lines):
        raw = lines[i].strip()
        if not raw or any(skip in raw for skip in skip_phrases):
            i += 1
            continue

        # Skip duplicate supplement lines (S01–S06)
        if raw.startswith(("S01", "S02", "S03", "S04", "S05", "S06")):
            if raw in seen_supplement_lines:
                i += 1
                continue
            seen_supplement_lines.add(raw)

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

        # Combine buffer with current line if needed
        if buffer:
            combined = f"{buffer} {raw}"
            norm = normalize_operation(combined)
            buffer = ""
        else:
            norm = normalize_operation(raw)

        # Only keep lines with a repair verb
        if re.search(verb_pattern, norm, flags=re.IGNORECASE):
            repair_lines.append(norm)

        i += 1

    return list(dict.fromkeys(repair_lines))  # Deduplicate while preserving order