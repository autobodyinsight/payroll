import re
import pdfplumber
from utils import normalize, normalize_operation

def merge_stacked_operations(lines: list[str]) -> list[str]:
    merged = []
    skip_next = False

    for i in range(len(lines)):
        if skip_next:
            skip_next = False
            continue

        current = lines[i].strip()
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

        current_clean = current.lower()
        next_clean = next_line.lower()

        if any(current_clean.endswith(op) for op in ["remove", "install"]) and re.search(r"/\s*(replace|install|remove)", next_clean):
            combined = f"{current} {next_line.strip()}"
            print(f"[MERGE] Combined stacked line: {combined}")
            merged.append(combined)
            skip_next = True
        else:
            merged.append(current)

    return merged

def extract_description(line: str) -> str:
    line = re.sub(r"[^a-zA-Z0-9\s\-&/]", "", line)
    line = re.sub(r"\d+(\.\d+)?$", "", line)
    return line.strip().title()

def parse_pdf(file_path: str) -> dict:
    raw_lines = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                raw_lines.extend(text.split('\n'))

    raw_lines = merge_stacked_operations(raw_lines)

    print("📄 Raw lines from PDF:")
    for line in raw_lines:
        print(f"[LINE] {line}")

    grouped = {"body": [], "paint": []}
    seen = set()
    headers = []

    for i, line in enumerate(raw_lines):
        norm = normalize(line)
        norm = normalize_operation(norm)

        if line.isupper() and len(line.strip().split()) <= 3:
            headers.append(line)
            continue

        # Match labor and optional paint hours at end of line
        match = re.search(r"(\d+(\.\d+)?)(\s+(\d+(\.\d+)?))?$", norm)
        if not match:
            continue

        description = extract_description(line)
        seen.add(norm)

        try:
            labor_time = float(match.group(1))
            grouped["body"].append({
                "operation": description,
                "labor_time": labor_time,
                "category": "body"
            })

            if match.group(4):
                paint_time = float(match.group(4))
                grouped["paint"].append({
                    "operation": description,
                    "labor_time": paint_time,
                    "category": "paint"
                })

        except ValueError:
            print(f"[ERROR] Could not parse labor/paint from line: {norm}")
            continue

    return {
        "raw_lines": raw_lines,
        "seen": seen,
        "headers": headers,
        "body": grouped["body"],
        "paint": grouped["paint"]
    }