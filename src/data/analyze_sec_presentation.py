import csv
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

NUM_FILE = BASE_DIR / "data" / "processed" / "sec_num_filtered.tsv"
PRE_FILE = BASE_DIR / "data" / "raw" / "sec" / "2025q2" / "pre.tsv"

# --------------------------------------------------
# Build (adsh, tag) -> statement types
# --------------------------------------------------

presentation = {}

with open(PRE_FILE, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        stmt = row["stmt"]
        tag = row["tag"]
        adsh = row["adsh"]

        if stmt in {"BS", "IS", "CF", "EQ"}:
            presentation[(adsh, tag)] = stmt

print(f"Presentation mappings: {len(presentation):,}")

# --------------------------------------------------
# Match consolidated NUM facts
# --------------------------------------------------

stmt_counts = Counter()
matched = 0
consolidated = 0

with open(NUM_FILE, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        if row["dimh"] != "0x00000000":
            continue

        consolidated += 1

        key = (row["adsh"], row["tag"])

        if key in presentation:
            stmt_counts[presentation[key]] += 1
            matched += 1

print("\n" + "=" * 50)
print("SEC PRESENTATION ANALYSIS")
print("=" * 50)

print(f"Consolidated NUM facts: {consolidated:,}")
print(f"Matched to BS/IS/CF/EQ: {matched:,}")

print("\nStatement distribution:")

for stmt, count in stmt_counts.most_common():
    print(f"{stmt}: {count:,}")