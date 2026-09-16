import json
with open(r"data\raw\train.json", "r", encoding="utf-8") as f:
    train_data = json.load(f)

empty_examples = []

for example in train_data:
    if not example["qa"]["answer"].strip():
        empty_examples.append(example)

for example in empty_examples:
    steps = example["qa"]["steps"]

    if steps:
        print(
            "Question:", example["qa"]["question"],
            "\nFinal result:", steps[-1]["res"],
            "\n---"
        )