import csv
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

SEC_DIR = BASE_DIR / "data" / "raw" / "sec" / "2025q2"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INDEX_FILE = PROCESSED_DIR / "sec_filing_index.csv"
NUM_FILE = SEC_DIR / "num.tsv"
PRE_FILE = SEC_DIR / "pre.tsv"
OUTPUT_FILE = PROCESSED_DIR / "sec_structured_v1.tsv"


VALID_STATEMENTS = {"BS", "IS", "CF", "EQ"}


# --------------------------------------------------
# 1. Load filing metadata
# --------------------------------------------------

filings = {}

with open(INDEX_FILE, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        filings[row["adsh"]] = row


print(f"Filing metadata loaded: {len(filings):,}")


# --------------------------------------------------
# 2. Load presentation metadata
# --------------------------------------------------

# (adsh, tag) -> set of statement types
presentation = defaultdict(set)

# (adsh, tag) -> human-readable labels
labels = defaultdict(set)

with open(PRE_FILE, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        stmt = row["stmt"]
        tag = row["tag"]

        if stmt not in VALID_STATEMENTS:
            continue

        # Ignore presentation-only concepts
        if tag.endswith("Abstract"):
            continue

        if tag in {
            "StatementLineItems",
            "StatementTable",
            "EquityComponentDomain",
        }:
            continue

        key = (row["adsh"], tag)

        presentation[key].add(stmt)

        if row["plabel"]:
            labels[key].add(row["plabel"])


print(f"Presentation mappings loaded: {len(presentation):,}")


# --------------------------------------------------
# 3. Stream NUM and build structured records
# --------------------------------------------------

fieldnames = [
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


rows_written = 0
rows_skipped = 0


with open(NUM_FILE, "r", encoding="utf-8", newline="") as fin:
    reader = csv.DictReader(fin, delimiter="\t")

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as fout:

        writer = csv.DictWriter(
            fout,
            fieldnames=fieldnames,
            delimiter="\t"
        )

        writer.writeheader()

        for row in reader:

            # Only consolidated/default facts
            if row["dimh"] != "0x00000000":
                continue

            key = (row["adsh"], row["tag"])

            # Must have financial-statement presentation
            if key not in presentation:
                rows_skipped += 1
                continue

            filing = filings.get(row["adsh"])

            if filing is None:
                rows_skipped += 1
                continue

            statements = sorted(presentation[key])

            # If a tag appears in multiple statements,
            # keep the statement information rather than
            # silently overwriting it.
            statement = "|".join(statements)

            label_values = sorted(labels.get(key, []))
            label = " | ".join(label_values)

            output_row = {
                "adsh": row["adsh"],
                "cik": filing["cik"],
                "company": filing["name"],
                "form": filing["form"],
                "period": filing["period"],
                "filed": filing["filed"],
                "statement": statement,
                "tag": row["tag"],
                "label": label,
                "ddate": row["ddate"],
                "qtrs": row["qtrs"],
                "uom": row["uom"],
                "value": row["value"],
            }

            writer.writerow(output_row)

            rows_written += 1

            if rows_written % 500_000 == 0:
                print(
                    f"Written {rows_written:,} structured facts..."
                )


print("\n" + "=" * 50)
print("SEC STRUCTURED DATASET COMPLETE")
print("=" * 50)

print(f"Rows written: {rows_written:,}")
print(f"Rows skipped: {rows_skipped:,}")
print(f"Saved to: {OUTPUT_FILE}")