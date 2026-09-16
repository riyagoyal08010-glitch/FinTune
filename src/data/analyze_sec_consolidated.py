import csv
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "processed" / "sec_num_filtered.tsv"

tag_counts = Counter()
row_count = 0

print("Reading consolidated SEC facts...")

with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        if row["dimh"] != "0x00000000":
            continue

        tag_counts[row["tag"]] += 1
        row_count += 1

        if row_count % 500_000 == 0:
            print(f"Processed {row_count:,} consolidated rows...")

print("\n" + "=" * 50)
print(f"Consolidated rows: {row_count:,}")
print("=" * 50)

print("\nTop 50 consolidated XBRL tags:")

for tag, count in tag_counts.most_common(50):
    print(f"{count:>10,}  {tag}")