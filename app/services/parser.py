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
        "authorization", "responsibility", "appraisal", "ACD", "NOTE:", "Adj.=", "Replace.", "Rpr=", "VIN=", "EPA=", "NHTSA="
    ]

    buffer = ""
    for line in lines:
        raw = line.strip()
        if not raw or any(skip in raw for skip in skip_phrases):
            continue

        # If line contains a repair verb and has context, keep it
        if re.search(verb_pattern, raw, flags=re.IGNORECASE):
            if len(raw.split()) > 1:
                repair_lines.append(raw)
            else:
                buffer = raw  # Save verb-only line
        elif buffer:
            # Combine previous verb-only line with this one
            combined = f"{buffer} {raw}"
            repair_lines.append(combined)
            buffer = ""

    return repair_lines