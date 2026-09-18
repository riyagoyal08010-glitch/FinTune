import csv
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "sec_num_consolidated_v1.tsv"
)

FACT_KEY_FIELDS = [
    "adsh",
    "tag",
    "ddate",
    "qtrs",
    "uom",
    "value",
    "iprx",
]

groups = defaultdict(list)

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        key = tuple(row[field] for field in FACT_KEY_FIELDS)

        groups[key].append(row)

        if len(groups[key]) == 2:

            print("\n" + "=" * 70)
            print("DUPLICATE IN CONSOLIDATED NUM DATASET")
            print("=" * 70)

            print("\nFact key:")
            for field in FACT_KEY_FIELDS:
                print(f"{field:10}: {row[field]}")

            for i, duplicate in enumerate(groups[key], start=1):

                print(f"\n--- Row {i} ---")

                for field, value in duplicate.items():
                    print(f"{field:20}: {value}")

            print("\n" + "=" * 70)
            print("INSPECTION COMPLETE")
            print("=" * 70)

            raise SystemExit

print("No duplicate found.")