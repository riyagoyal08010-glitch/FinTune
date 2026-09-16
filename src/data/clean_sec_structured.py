import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "sec_structured_v1.tsv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "sec_structured_v1_clean.tsv"
)


rows_read = 0
rows_removed = 0
rows_written = 0


with open(
    INPUT_FILE,
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
            fieldnames=reader.fieldnames,
            delimiter="\t"
        )

        writer.writeheader()

        for row in reader:

            rows_read += 1

            # Numeric facts without a value are unusable.
            if not row["value"].strip():
                rows_removed += 1
                continue

            # Missing presentation label is acceptable because
            # the XBRL tag is still available.
            if not row["label"].strip():
                row["label"] = row["tag"]

            writer.writerow(row)
            rows_written += 1


print("\n" + "=" * 50)
print("SEC STRUCTURED DATASET CLEANING")
print("=" * 50)

print(f"Rows read:       {rows_read:,}")
print(f"Rows removed:    {rows_removed:,}")
print(f"Rows written:    {rows_written:,}")

print(f"\nSaved to:")
print(OUTPUT_FILE)

print("\nReason for removal:")
print("Missing numeric value")

print("\nLabel fallback:")
print("Missing label -> XBRL tag")