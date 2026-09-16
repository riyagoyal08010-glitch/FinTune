import json
from pathlib import Path


# -------------------------
# Paths 
# -------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_FILE = BASE_DIR /"FinTune" / "data" / "raw" / "train.json"
OUTPUT_FILE = BASE_DIR /"FinTune" / "data" / "processed" / "finqa_clean.json"


# -------------------------
# Load dataset
# -------------------------

with open(RAW_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loaded {len(data)} examples")


# -------------------------
# Process examples
# -------------------------

processed_data = []

for example in data:

    qa = example["qa"]

    question = qa["question"].strip()

    # Use answer if available
    answer = qa["answer"].strip()

    # Recover missing answers
    if not answer and qa.get("steps"):
        answer = qa["steps"][-1]["res"].strip()

    # Supporting evidence
    gold_inds = qa.get("gold_inds", {})

    evidence = list(gold_inds.values())

    # Reasoning program
    program = qa.get("program", "")

    # Store cleaned example
    processed_example = {
        "question": question,
        "answer": answer,
        "evidence": evidence,
        "program": program,
    }

    processed_data.append(processed_example)


# -------------------------
# Save processed dataset
# -------------------------

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(processed_data, f, indent=2, ensure_ascii=False)


print(f"Saved {len(processed_data)} examples")
print(f"Output: {OUTPUT_FILE}")