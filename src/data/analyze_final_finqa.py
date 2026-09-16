import json
import re
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parents[2]

TRAIN_FILE = BASE_DIR / "data" / "processed" / "finqa_sft_train.json"
DEV_FILE = BASE_DIR / "data" / "processed" / "finqa_sft_dev.json"


def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def word_count(text):
    return len(text.split())


def program_operations(program):
    operations = [
        "add",
        "subtract",
        "multiply",
        "divide",
        "greater",
        "table_average",
        "table_max",
        "table_min",
        "table_sum",
        "exp",
    ]

    found = []

    for operation in operations:
        found.extend(
            re.findall(
                rf"\b{operation}\(",
                program
            )
        )

    return [
        operation[:-1]
        for operation in found
    ]


def analyze_split(name, data):

    print("\n" + "=" * 60)
    print(f"{name} DATASET")
    print("=" * 60)

    print(f"Examples: {len(data)}")

    # --------------------------------------------------------
    # Question length
    # --------------------------------------------------------

    question_lengths = [
        word_count(x["question"])
        for x in data
    ]

    print("\nQuestion length:")
    print(
        f"  Average: "
        f"{sum(question_lengths) / len(question_lengths):.2f}"
    )
    print(f"  Minimum: {min(question_lengths)}")
    print(f"  Maximum: {max(question_lengths)}")

    # --------------------------------------------------------
    # Answer types
    # --------------------------------------------------------

    answer_types = Counter()

    for example in data:

        answer = example["answer"].strip().lower()

        if answer in {"yes", "no"}:
            answer_types["yes/no"] += 1

        elif "%" in answer:
            answer_types["percentage"] += 1

        elif re.fullmatch(
            r"-?\d+(\.\d+)?",
            answer.replace(",", "")
        ):
            answer_types["numeric"] += 1

        else:
            answer_types["other"] += 1

    print("\nAnswer types:")

    for answer_type, count in answer_types.most_common():
        percentage = count / len(data) * 100
        print(
            f"  {answer_type}: "
            f"{count} ({percentage:.2f}%)"
        )

    # --------------------------------------------------------
    # Evidence statistics
    # --------------------------------------------------------

    evidence_counts = [
        len(x["evidence"])
        for x in data
    ]

    evidence_lengths = [
        sum(word_count(e) for e in x["evidence"])
        for x in data
    ]

    print("\nEvidence:")
    print(
        f"  Average evidence items: "
        f"{sum(evidence_counts) / len(evidence_counts):.2f}"
    )
    print(
        f"  Maximum evidence items: "
        f"{max(evidence_counts)}"
    )

    print(
        f"  Average evidence words: "
        f"{sum(evidence_lengths) / len(evidence_lengths):.2f}"
    )

    print(
        f"  Maximum evidence words: "
        f"{max(evidence_lengths)}"
    )

    # --------------------------------------------------------
    # Program complexity
    # --------------------------------------------------------

    program_lengths = []

    operation_counts = Counter()

    for example in data:

        operations = program_operations(
            example["program"]
        )

        program_lengths.append(len(operations))

        operation_counts.update(operations)

    print("\nProgram complexity:")
    print(
        f"  Average operations/example: "
        f"{sum(program_lengths) / len(program_lengths):.2f}"
    )
    print(
        f"  Maximum operations/example: "
        f"{max(program_lengths)}"
    )

    print("\nOperation frequency:")

    total_operations = sum(operation_counts.values())

    for operation, count in operation_counts.most_common():

        percentage = count / total_operations * 100

        print(
            f"  {operation}: "
            f"{count} ({percentage:.2f}%)"
        )

    # --------------------------------------------------------
    # Multi-step reasoning
    # --------------------------------------------------------

    complexity_distribution = Counter(
        program_lengths
    )

    print("\nOperations per example:")

    for number_of_operations in sorted(
        complexity_distribution
    ):

        count = complexity_distribution[
            number_of_operations
        ]

        percentage = count / len(data) * 100

        print(
            f"  {number_of_operations} operation(s): "
            f"{count} ({percentage:.2f}%)"
        )


def compare_train_dev(train, dev):

    print("\n" + "=" * 60)
    print("TRAIN vs DEV")
    print("=" * 60)

    train_questions = {
        x["question"].strip().lower()
        for x in train
    }

    dev_questions = {
        x["question"].strip().lower()
        for x in dev
    }

    overlap = train_questions & dev_questions

    print(
        f"Exact question overlap: "
        f"{len(overlap)}"
    )

    print("\nThis is NOT automatically leakage.")
    print(
        "Same questions can appear with different "
        "financial contexts."
    )


if __name__ == "__main__":

    train = load_data(TRAIN_FILE)
    dev = load_data(DEV_FILE)

    analyze_split("TRAIN", train)
    analyze_split("DEV", dev)

    compare_train_dev(train, dev)

    print("\n" + "=" * 60)
    print("FINAL FINQA ANALYSIS COMPLETE")
    print("=" * 60)