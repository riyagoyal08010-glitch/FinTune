import csv
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "sec_structured_v1_clean.tsv"
)

TARGET_TAGS = {
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "NetIncomeLoss",
    "ProfitLoss",
    "OperatingIncomeLoss",
    "Assets",
    "Liabilities",
    "StockholdersEquity",
}

SAMPLES_PER_TAG = 5

samples = defaultdict(list)


with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        tag = row["tag"]

        if tag not in TARGET_TAGS:
            continue

        if len(samples[tag]) >= SAMPLES_PER_TAG:
            continue

        samples[tag].append({
            "company": row["company"],
            "form": row["form"],
            "period": row["period"],
            "statement": row["statement"],
            "label": row["label"],
            "ddate": row["ddate"],
            "qtrs": row["qtrs"],
            "uom": row["uom"],
            "value": row["value"],
        })


print("\n" + "=" * 70)
print("SEC CONCEPT INSPECTION")
print("=" * 70)


for tag in sorted(TARGET_TAGS):

    print(f"\n{'-' * 70}")
    print(f"TAG: {tag}")
    print(f"{'-' * 70}")

    for i, sample in enumerate(samples[tag], start=1):

        print(f"\nSample {i}")

        for key, value in sample.items():
            print(f"  {key:10}: {value}")


print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)