import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"


SYSTEM_PROMPT = (
    "You are a financial reasoning assistant. "
    "Answer the financial question using the provided evidence "
    "and perform the necessary calculation."
)


def convert_example(example):
    evidence = "\n".join(
        f"- {item}" for item in example["evidence"]
    )

    user_message = (
        f"Question: {example['question']}\n\n"
        f"Evidence:\n{evidence}"
    )

    return {
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_message,
            },
            {
                "role": "assistant",
                "content": example["answer"],
            },
        ]
    }


def convert_dataset(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    chat_data = [convert_example(example) for example in data]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, indent=2, ensure_ascii=False)

    print(f"Input examples:  {len(data)}")
    print(f"Output examples: {len(chat_data)}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    train_input = PROCESSED_DIR / "dataset_v2_train.json"
    dev_input = PROCESSED_DIR / "dataset_v2_dev.json"

    train_output = PROCESSED_DIR / "dataset_v2_chat_train.json"
    dev_output = PROCESSED_DIR / "dataset_v2_chat_dev.json"

    print("\n=== Converting training dataset ===")
    convert_dataset(train_input, train_output)

    print("\n=== Converting development dataset ===")
    convert_dataset(dev_input, dev_output)

    print("\nChat dataset preparation complete.")