import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

SEC_DIR = BASE_DIR / "data" / "raw" / "sec" / "2025q2"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INDEX_FILE = PROCESSED_DIR / "sec_filing_index.csv"
NUM_FILE = SEC_DIR / "num.tsv"
OUTPUT_FILE = PROCESSED_DIR / "sec_num_filtered.tsv"


# --------------------------------------------------
# 1. Load filing IDs we actually care about
# --------------------------------------------------

filing_ids = set()

with open(INDEX_FILE, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        filing_ids.add(row["adsh"])

print(f"Target filings: {len(filing_ids)}")


# --------------------------------------------------
# 2. Stream NUM and keep only target filings
# --------------------------------------------------

rows_kept = 0

with open(NUM_FILE, "r", encoding="utf-8", newline="") as fin:
    reader = csv.DictReader(fin, delimiter="\t")

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as fout:

        writer = csv.DictWriter(
            fout,
            fieldnames=reader.fieldnames,
            delimiter="\t"
        )

        writer.writeheader()

        for row in reader:

            if row["adsh"] in filing_ids:
                writer.writerow(row)
                rows_kept += 1

print(f"Numeric rows kept: {rows_kept}")
print(f"Saved to: {OUTPUT_FILE}")