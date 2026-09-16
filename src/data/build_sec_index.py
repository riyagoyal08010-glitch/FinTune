import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

SEC_DIR = BASE_DIR / "data" / "raw" / "sec" / "2025q2"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SUB_FILE = SEC_DIR / "sub.tsv"
OUTPUT_FILE = OUTPUT_DIR / "sec_filing_index.csv"

KEEP_FORMS = {
    "10-Q",
    "10-Q/A",
    "10-K",
    "10-K/A",
    "20-F",
    "20-F/A",
}

rows = []

with open(SUB_FILE, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        if row["form"] not in KEEP_FORMS:
            continue

        rows.append({
            "adsh": row["adsh"],
            "cik": row["cik"],
            "name": row["name"],
            "form": row["form"],
            "period": row["period"],
            "filed": row["filed"],
        })

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "adsh",
            "cik",
            "name",
            "form",
            "period",
            "filed",
        ],
    )

    writer.writeheader()
    writer.writerows(rows)

print(f"Saved: {OUTPUT_FILE}")
print(f"Filings: {len(rows)}")