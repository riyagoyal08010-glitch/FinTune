import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "sec_num_consolidated_v2.tsv"
)

FACT_KEY_FIELDS = [
    "adsh",
    "tag",
    "ddate",
    "qtrs",
    "uom",
    "value",
]

seen = set()
duplicates = 0

with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        key = tuple(row[field] for field in FACT_KEY_FIELDS)

        if key in seen:
            duplicates += 1

            if duplicates <= 3:
                print("\nDUPLICATE:")
                for field in FACT_KEY_FIELDS:
                    print(f"{field}: {row[field]}")

        else:
            seen.add(key)

print("\n" + "=" * 60)
print(f"Rows: {len(seen) + duplicates:,}")
print(f"Duplicate rows: {duplicates:,}")
print("=" * 60)