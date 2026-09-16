import csv
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "FinTune"/ "data" / "processed" / "sec_num_filtered.tsv"

counts = Counter()

with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        if row["dimh"]:
            counts["dimensioned"] += 1
        else:
            counts["undimensioned"] += 1

print(counts)