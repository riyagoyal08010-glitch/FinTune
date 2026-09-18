import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "sec_num_filtered.tsv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "sec_num_consolidated_v2.tsv"
)


FACT_KEY_FIELDS = [
    "adsh",
    "tag",
    "ddate",
    "qtrs",
    "uom",
    "value",
   
]


rows_read = 0
rows_kept = 0
rows_skipped_dimensioned = 0
duplicates_removed = 0

seen = set()


print("Building consolidated SEC NUM dataset...")


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8",
    newline=""
) as fin:

    reader = csv.DictReader(
        fin,
        delimiter="\t"
    )

    fieldnames = reader.fieldnames

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

            rows_read += 1

            # Keep only consolidated/default facts.
            if row["dimh"] != "0x00000000":
                rows_skipped_dimensioned += 1
                continue

            key = tuple(
                row[field]
                for field in FACT_KEY_FIELDS
            )

            if key in seen:
                duplicates_removed += 1
                continue

            seen.add(key)

            writer.writerow(row)

            rows_kept += 1


print("\n" + "=" * 60)
print("SEC CONSOLIDATED NUM DATASET")
print("=" * 60)

print(f"Rows read:                    {rows_read:,}")
print(
    f"Dimensioned rows skipped:     "
    f"{rows_skipped_dimensioned:,}"
)
print(
    f"Duplicate rows removed:       "
    f"{duplicates_removed:,}"
)
print(f"Rows kept:                    {rows_kept:,}")

print(f"\nSaved to:")
print(OUTPUT_FILE)

print("\n" + "=" * 60)
print("BUILD COMPLETE")
print("=" * 60)