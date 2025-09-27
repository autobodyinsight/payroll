import re
from collections import defaultdict

def parse_estimate(text: str):
    lines = text.splitlines()
    grouped = defaultdict(list)

    labor_col = None
    paint_col = None

    for i, line in enumerate(lines):
        if "labor" in line.lower() and "paint" in line.lower():
            # Identify column positions from header line
            labor_col = line.lower().index("labor")
            paint_col = line.lower().index("paint")
            continue

        if labor_col is None or paint_col is None:
            continue  # Skip until header is found

        if len(line) < max(labor_col, paint_col):
            continue  # Skip malformed lines

        labor_str = line[labor_col:paint_col].strip()
        paint_str = line[paint_col:].strip()
        description = line[:labor_col].strip()

        labor_time = extract_hours(labor_str)
        paint_time = extract_hours(paint_str)

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

def extract_hours(value: str):
    match = re.search(r"\d+(\.\d+)?", value)
    return float(match.group()) if match else None