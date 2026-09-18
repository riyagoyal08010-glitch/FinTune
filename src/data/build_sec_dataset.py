import csv
from pathlib import Path
from collections import defaultdict


BASE_DIR = Path(__file__).resolve().parents[2]

SEC_DIR = BASE_DIR / "data" / "raw" / "sec" / "2025q2"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INDEX_FILE = PROCESSED_DIR / "sec_filing_index.csv"
PRE_FILE = SEC_DIR / "pre.tsv"
NUM_FILE = PROCESSED_DIR / "sec_num_consolidated_v2.tsv"

OUTPUT_FILE = (
    PROCESSED_DIR
    / "sec_structured_v3.tsv"
)


VALID_STATEMENTS = {"BS", "IS", "CF", "EQ"}

PRESENTATION_ONLY_TAGS = {
    "StatementLineItems",
    "StatementTable",
    "EquityComponentDomain",
}


# ---------------------------------------------------------
# 1. Load filing metadata
# ---------------------------------------------------------

filings = {}

with open(
    INDEX_FILE,
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(f)

    for row in reader:
        filings[row["adsh"]] = {
            "cik": row["cik"],
            "company": row["name"],
            "form": row["form"],
            "period": row["period"],
            "filed": row["filed"],
        }


print(f"Filing metadata loaded: {len(filings):,}")


# ---------------------------------------------------------
# 2. Load PRE presentation metadata
#
# IMPORTANT:
# Use sets so repeated PRE rows don't duplicate facts.
# ---------------------------------------------------------

presentation = defaultdict(
    lambda: {
        "statements": set(),
        "labels": set(),
    }
)


with open(
    PRE_FILE,
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        adsh = row["adsh"]
        tag = row["tag"]
        stmt = row["stmt"]
        label = row["plabel"]

        if stmt not in VALID_STATEMENTS:
            continue

        if tag in PRESENTATION_ONLY_TAGS:
            continue

        if tag.endswith("Abstract"):
            continue

        key = (adsh, tag)

        presentation[key]["statements"].add(stmt)

        if label.strip():
            presentation[key]["labels"].add(label.strip())


print(
    f"Presentation mappings loaded: "
    f"{len(presentation):,}"
)


# ---------------------------------------------------------
# 3. Stream NUM and join with PRE + filing metadata
# ---------------------------------------------------------

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


with open(
    NUM_FILE,
    "r",
    encoding="utf-8",
    newline=""
) as fin:

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

            # Only consolidated/default dimension.
            if row["dimh"] != "0x00000000":
                rows_skipped += 1
                continue

            adsh = row["adsh"]
            tag = row["tag"]

            # Need filing metadata.
            if adsh not in filings:
                rows_skipped += 1
                continue

            # Need statement presentation.
            key = (adsh, tag)

            if key not in presentation:
                rows_skipped += 1
                continue

            # Missing numeric values are unusable.
            if not row["value"].strip():
                rows_skipped += 1
                continue

            metadata = filings[adsh]
            presentation_data = presentation[key]

            statements = "|".join(
                sorted(presentation_data["statements"])
            )

            labels = "|".join(
                sorted(presentation_data["labels"])
            )

            # Fallback to XBRL tag if presentation
            # label is unavailable.
            if not labels:
                labels = tag

            writer.writerow({
                "adsh": adsh,
                "cik": metadata["cik"],
                "company": metadata["company"],
                "form": metadata["form"],
                "period": metadata["period"],
                "filed": metadata["filed"],
                "statement": statements,
                "tag": tag,
                "label": labels,
                "ddate": row["ddate"],
                "qtrs": row["qtrs"],
                "uom": row["uom"],
                "value": row["value"],
            })

            rows_written += 1

            if rows_written % 500_000 == 0:
                print(
                    f"Written {rows_written:,} rows..."
                )


print("\n" + "=" * 60)
print("SEC STRUCTURED DATASET V2")
print("=" * 60)

print(
    f"Filing metadata:       {len(filings):,}"
)

print(
    f"Presentation mappings: {len(presentation):,}"
)

print(
    f"Rows written:          {rows_written:,}"
)

print(
    f"Rows skipped:          {rows_skipped:,}"
)

print(f"\nSaved to:\n{OUTPUT_FILE}")

print("\n" + "=" * 60)
print("BUILD COMPLETE")
print("=" * 60)