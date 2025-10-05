import re

REPAIR_VERBS = [
    "rpr", "repl", "r&i", "blnd", "repair", "replace", "remove", "install",
    "add for", "aim", "o/h", "adjust", "set", "calibrate"
]

def normalize(text: str) -> str:
    """
    Basic normalization: lowercase, strip whitespace, collapse multiple spaces.
    """
    if not text:
        return ""
    text = text.lower()
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text

def normalize_operation(text: str) -> str:
    """
    Normalize operation line by removing duplicate verbs and trimming.
    """
    text = normalize(text)
    for verb in REPAIR_VERBS:
        # Remove repeated verbs like "r&i r&i"
        pattern = rf"\b({verb})\b\s+\1\b"
        text = re.sub(pattern, r"\1", text)
    return text.strip()