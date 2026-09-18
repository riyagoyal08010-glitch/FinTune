import json
import random
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

FINQA_TRAIN = (
    BASE_DIR
    / "data"
    / "processed"
    / "finqa_sft_train.json"
)

FINQA_DEV = (
    BASE_DIR
    / "data"
    / "processed"
    / "finqa_sft_dev.json"
)

SEC_DATA = (
    BASE_DIR
    / "data"
    / "processed"
    / "sec_reasoning_v1.json"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"

TRAIN_OUTPUT = OUTPUT_DIR / "dataset_v2_train.json"
DEV_OUTPUT = OUTPUT_DIR / "dataset_v2_dev.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


print("Loading datasets...")

finqa_train = load_json(FINQA_TRAIN)
finqa_dev = load_json(FINQA_DEV)
sec_data = load_json(SEC_DATA)

print(f"FinQA train: {len(finqa_train):,}")
print(f"FinQA dev:   {len(finqa_dev):,}")
print(f"SEC:         {len(sec_data):,}")


# ---------------------------------------------------------
# Normalize SEC examples to FinQA-style fields
# ---------------------------------------------------------

sec_normalized = []

for example in sec_data:

    sec_normalized.append({
        "instruction": example["instruction"],
        "question": example["question"],
        "evidence": example["evidence"],
        "calculation": example["calculation"],
        "answer": example["answer"],
        "source": "SEC",
    })


# ---------------------------------------------------------
# Keep FinQA train/dev split
# Add SEC examples only to TRAIN
# ---------------------------------------------------------

train_data = []

for example in finqa_train:

    train_data.append({
        **example,
        "source": "FinQA",
    })

train_data.extend(sec_normalized)


dev_data = []

for example in finqa_dev:

    dev_data.append({
        **example,
        "source": "FinQA",
    })


# ---------------------------------------------------------
# Shuffle training data
# ---------------------------------------------------------

random.seed(42)
random.shuffle(train_data)


# ---------------------------------------------------------
# Validate
# ---------------------------------------------------------

required_fields = [
    "instruction",
    "question",
    "evidence",
    "answer",
    "source",
]


def validate(data, name):

    errors = 0

    for i, example in enumerate(data):

        for field in required_fields:

            if field not in example:
                print(
                    f"{name}: missing '{field}' "
                    f"at index {i}"
                )
                errors += 1

        if not example["question"]:
            errors += 1

        if not example["answer"]:
            errors += 1

        if not example["evidence"]:
            errors += 1

    print(
        f"{name} validation errors: {errors}"
    )

    return errors == 0


train_valid = validate(train_data, "TRAIN")
dev_valid = validate(dev_data, "DEV")


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

with open(
    TRAIN_OUTPUT,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        train_data,
        f,
        indent=2,
        ensure_ascii=False
    )


with open(
    DEV_OUTPUT,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        dev_data,
        f,
        indent=2,
        ensure_ascii=False
    )


print("\n" + "=" * 60)
print("DATASET V2 COMPLETE")
print("=" * 60)

print(f"Train examples: {len(train_data):,}")
print(f"Dev examples:   {len(dev_data):,}")

print(f"\nTrain saved to:")
print(TRAIN_OUTPUT)

print(f"\nDev saved to:")
print(DEV_OUTPUT)

print("\nValidation:")
print(f"Train valid: {train_valid}")
print(f"Dev valid:   {dev_valid}")

print("=" * 60)