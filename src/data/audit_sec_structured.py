import csv
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "sec_structured_v1.tsv"
)

FIELDS = [
    "adsh",
    "cik",
    "company",
    "form",
    "period",
    "filed",
    "statement",
    "tag",
    "label",
    "ddate",
    "qtrs",
    "uom",
    "value",
]


missing_fields = Counter()
qtrs = Counter()

rows = 0
filings = set()
companies = set()
tags = set()


with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:

    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        rows += 1

        for field in FIELDS:
            if not row[field].strip():
                missing_fields[field] += 1

        qtrs[row["qtrs"]] += 1

        filings.add(row["adsh"])
        companies.add(row["cik"])
        tags.add(row["tag"])


print("\n" + "=" * 50)
print("SEC STRUCTURED DATASET DIAGNOSTIC")
print("=" * 50)

print(f"Rows:              {rows:,}")
print(f"Unique filings:    {len(filings):,}")
print(f"Unique companies:  {len(companies):,}")
print(f"Unique tags:       {len(tags):,}")

print("\nMissing values by field:")

for field, count in missing_fields.most_common():
    print(f"  {field}: {count:,}")


print("\nQtrs distribution:")

normal_qtrs = {
    key: value
    for key, value in qtrs.items()
    if key.isdigit() and int(key) <= 4
}

unusual_qtrs = {
    key: value
    for key, value in qtrs.items()
    if not key.isdigit() or int(key) > 4
}

for key, value in sorted(
    normal_qtrs.items(),
    key=lambda x: int(x[0])
):
    print(f"  {key}: {value:,}")

print("\nUnusual qtrs:")

for key, value in sorted(
    unusual_qtrs.items(),
    key=lambda x: int(x[0]) if x[0].isdigit() else 999
):
    print(f"  {key}: {value:,}")

print("\n" + "=" * 50)