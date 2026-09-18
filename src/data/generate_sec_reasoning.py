import csv
import json
import random
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "processed" / "sec_structured_v3.tsv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "sec_reasoning_v1.json"

TARGET_COMPANIES = 2000
MAX_EXAMPLES = 10000

TARGET_TAGS = {
    "RevenueFromContractWithCustomerExcludingAssessedTax": "revenue",
    "Revenues": "revenue",
    "OperatingIncomeLoss": "operating_income",
    "NetIncomeLoss": "net_income",
    "Assets": "assets",
    "Liabilities": "liabilities",
    "StockholdersEquity": "equity",
}

facts = defaultdict(dict)

print("Loading SEC facts...")

with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        tag = row["tag"]

        if tag not in TARGET_TAGS:
            continue

        try:
            value = float(row["value"])
        except ValueError:
            continue

        key = (
            row["adsh"],
            row["ddate"],
            row["qtrs"],
            TARGET_TAGS[tag],
        )

        facts[key] = {
            "company": row["company"],
            "adsh": row["adsh"],
            "date": row["ddate"],
            "qtrs": row["qtrs"],
            "concept": TARGET_TAGS[tag],
            "tag": tag,
            "label": row["label"],
            "value": value,
            "uom": row["uom"],
        }

print(f"Useful fact groups: {len(facts):,}")


# ---------------------------------------------------------
# Group facts by filing + date
# ---------------------------------------------------------

groups = defaultdict(dict)

for fact in facts.values():
    group_key = (
        fact["adsh"],
        fact["date"],
        fact["qtrs"],
    )

    groups[group_key][fact["concept"]] = fact


# ---------------------------------------------------------
# Generate reasoning examples
# ---------------------------------------------------------

examples = []

for group_key, data in groups.items():

    company = next(iter(data.values()))["company"]

    # Revenue + operating income -> operating margin
    if "revenue" in data and "operating_income" in data:

        revenue = data["revenue"]["value"]
        operating_income = data["operating_income"]["value"]

        if revenue != 0:

            margin = operating_income / revenue * 100

            examples.append({
                "instruction": (
                    "Answer the financial question using "
                    "the provided financial evidence and calculation."
                ),
                "question": (
                    f"What is the operating margin for {company}?"
                ),
                "evidence": [
                    f"Revenue: {revenue}",
                    f"Operating income: {operating_income}",
                ],
                "calculation": (
                    "Operating margin = "
                    "Operating income / Revenue × 100"
                ),
                "answer": f"{margin:.2f}%",
                "source": "SEC",
            })

    # Revenue + net income -> net margin
    if "revenue" in data and "net_income" in data:

        revenue = data["revenue"]["value"]
        net_income = data["net_income"]["value"]

        if revenue != 0:

            margin = net_income / revenue * 100

            examples.append({
                "instruction": (
                    "Answer the financial question using "
                    "the provided financial evidence and calculation."
                ),
                "question": (
                    f"What is the net profit margin for {company}?"
                ),
                "evidence": [
                    f"Revenue: {revenue}",
                    f"Net income: {net_income}",
                ],
                "calculation": (
                    "Net margin = "
                    "Net income / Revenue × 100"
                ),
                "answer": f"{margin:.2f}%",
                "source": "SEC",
            })

    # Assets - liabilities -> equity relationship
    if "assets" in data and "liabilities" in data:

        assets = data["assets"]["value"]
        liabilities = data["liabilities"]["value"]

        implied_equity = assets - liabilities

        examples.append({
            "instruction": (
                "Answer the financial question using "
                "the provided financial evidence and calculation."
            ),
            "question": (
                f"What is the implied equity for {company}?"
            ),
            "evidence": [
                f"Assets: {assets}",
                f"Liabilities: {liabilities}",
            ],
            "calculation": (
                "Implied equity = Assets - Liabilities"
            ),
            "answer": f"{implied_equity:.2f}",
            "source": "SEC",
        })


# ---------------------------------------------------------
# Shuffle + limit
# ---------------------------------------------------------

random.seed(42)
random.shuffle(examples)

examples = examples[:MAX_EXAMPLES]

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        examples,
        f,
        indent=2,
        ensure_ascii=False
    )

print("\n" + "=" * 60)
print("SEC REASONING DATASET")
print("=" * 60)

print(f"Examples generated: {len(examples):,}")
print(f"Saved to: {OUTPUT_FILE}")