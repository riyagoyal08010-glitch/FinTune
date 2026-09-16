import csv
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "sec_structured_v1_clean.tsv"
)

rows = 0
missing = Counter()
qtrs = Counter()
statements = Counter()

with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")

    required_fields = reader.fieldnames

    for row in reader:
        rows += 1

        for field in required_fields:
            if not row[field].strip():
                missing[field] += 1

        qtrs[row["qtrs"]] += 1
        statements[row["statement"]] += 1


print("\n" + "=" * 50)
print("FINAL SEC DATASET AUDIT")
print("=" * 50)

print(f"Rows: {rows:,}")

print("\nMissing values:")
if not missing:
    print("None")
else:
    for field, count in missing.items():
        print(f"  {field}: {count:,}")

print("\nStatement distribution:")
for statement, count in statements.most_common():
    print(f"  {statement}: {count:,}")

print("\nQtrs distribution:")
for value, count in sorted(
    qtrs.items(),
    key=lambda x: int(x[0]) if x[0].isdigit() else 999
):
    print(f"  {value}: {count:,}")

print("\n" + "=" * 50)

if not missing:
    print("AUDIT PASSED")
else:
    print("AUDIT FAILED")