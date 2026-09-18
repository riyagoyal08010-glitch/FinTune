import csv
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "sec_structured_v2.tsv"
)


# These fields identify the consolidated SEC fact
# in our v2 dataset.
FACT_KEY_FIELDS = [
    "adsh",
    "tag",
    "ddate",
    "qtrs",
    "uom",
    "value",
]


rows = 0
fact_keys = Counter()
exact_rows = Counter()

duplicate_examples = []


print("Reading SEC structured v2 dataset...")


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(
        f,
        delimiter="\t"
    )

    for row in reader:

        rows += 1

        # Exact complete-row duplicate
        exact_key = tuple(
            row[field]
            for field in reader.fieldnames
        )

        exact_rows[exact_key] += 1

        # Underlying consolidated fact
        fact_key = tuple(
            row[field]
            for field in FACT_KEY_FIELDS
        )

        fact_keys[fact_key] += 1

        # Save a few examples
        if (
            fact_keys[fact_key] == 2
            and len(duplicate_examples) < 10
        ):
            duplicate_examples.append(row)


# ---------------------------------------------------------
# Calculate duplicate statistics
# ---------------------------------------------------------

exact_duplicate_groups = sum(
    1
    for count in exact_rows.values()
    if count > 1
)

exact_duplicate_rows = sum(
    count - 1
    for count in exact_rows.values()
    if count > 1
)


fact_duplicate_groups = sum(
    1
    for count in fact_keys.values()
    if count > 1
)

fact_duplicate_rows = sum(
    count - 1
    for count in fact_keys.values()
    if count > 1
)


# ---------------------------------------------------------
# Print results
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("SEC STRUCTURED V2 DUPLICATE AUDIT")
print("=" * 60)

print(
    f"Total rows:                 "
    f"{rows:,}"
)

print("\nExact duplicate rows:")

print(
    f"  Duplicate groups:         "
    f"{exact_duplicate_groups:,}"
)

print(
    f"  Extra duplicate rows:     "
    f"{exact_duplicate_rows:,}"
)

print("\nDuplicate SEC fact keys:")

print(
    f"  Duplicate groups:         "
    f"{fact_duplicate_groups:,}"
)

print(
    f"  Extra duplicate rows:     "
    f"{fact_duplicate_rows:,}"
)


# ---------------------------------------------------------
# Examples
# ---------------------------------------------------------

if duplicate_examples:

    print("\nExample duplicate facts:")

    for i, row in enumerate(
        duplicate_examples,
        start=1
    ):

        print(f"\nExample {i}")

        for field in FACT_KEY_FIELDS:
            print(
                f"  {field:8}: "
                f"{row[field]}"
            )

        print(
            f"  company  : "
            f"{row['company']}"
        )

        print(
            f"  form     : "
            f"{row['form']}"
        )

        print(
            f"  period   : "
            f"{row['period']}"
        )

        print(
            f"  statement: "
            f"{row['statement']}"
        )

        print(
            f"  label    : "
            f"{row['label']}"
        )

else:

    print(
        "\nNo duplicate SEC facts found."
    )


print("\n" + "=" * 60)
print("DUPLICATE AUDIT COMPLETE")
print("=" * 60)