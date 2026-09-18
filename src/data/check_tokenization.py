from pathlib import Path
import json
from transformers import AutoTokenizer

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = Path(r"D:\FinTune\models\llama-3.2-3b-instruct")
DATA_FILE = BASE_DIR / "data" / "processed" / "dataset_v2_chat_train.json"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

# Load one training example
with open(DATA_FILE, "r", encoding="utf-8") as f:
    example = json.load(f)[0]

messages = example["messages"]

# Apply Llama's official chat template
formatted_text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=False,
)

# Tokenize
tokenized = tokenizer(
    formatted_text,
    return_tensors="pt",
)

print("\n===== MESSAGES =====")
for message in messages:
    print(f"\n[{message['role'].upper()}]")
    print(message["content"])

print("\n===== CHAT TEMPLATE OUTPUT =====")
print(formatted_text)

print("\n===== TOKENIZATION =====")
print("Number of tokens:", tokenized["input_ids"].shape[1])
print("First 30 token IDs:", tokenized["input_ids"][0][:30].tolist())

print("\n===== TOKENS =====")
print(tokenizer.convert_ids_to_tokens(tokenized["input_ids"][0][:30]))